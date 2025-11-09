#!/usr/bin/env python
import sys
import warnings
from typing import Optional
from datetime import datetime
import time
import asyncio

from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel

from firstone.crew import Firstone

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


class ResearchFlowState(BaseModel):
    """State model for the research flow"""
    topic: str = ""
    current_year: str = ""
    research_result: str = ""
    feedback: Optional[str] = None
    valid: bool = False
    retry_count: int = 0


class ResearchFlow(Flow[ResearchFlowState]):
    """Flow for iterative research-review-synthesis workflow"""

    @start("retry")
    def generate_research(self):
        """Generate research with researcher agent"""
        print(f"\n{'='*80}")
        print(f"📚 ITERATION {self.state.retry_count + 1} - Running Research Task")
        print(f"{'='*80}\n")
        
        # Add delay between retries to respect API rate limits
        if self.state.retry_count > 0:
            delay = 10  # 10 seconds delay between retries
            print(f"⏱️  Waiting {delay} seconds before retry to respect API rate limits...")
            time.sleep(delay)
        
        # Prepare inputs with feedback if available
        inputs = {
            "topic": self.state.topic,
            "current_year": self.state.current_year
        }
        
        if self.state.feedback:
            inputs["feedback"] = f"""
                PREVIOUS ATTEMPT WAS REJECTED (Attempt {self.state.retry_count}).

You MUST address the reviewer's feedback and improve your research significantly.

REVIEWER FEEDBACK:
{self.state.feedback}

FOCUS ON THESE IMPROVEMENTS:
- Address the specific issues mentioned in the feedback above
- Ensure you have 5-7 high-quality papers
- Make sure all papers are relevant to {self.state.topic}
- Provide clear explanations of methodology and findings (50+ words each)
- Use credible sources (ArXiv, peer-reviewed journals, conferences)

This is attempt {self.state.retry_count + 1} of 3. Make it count!
"""
        
        # Create research crew (researcher only)
        from crewai import Crew, Process
        research_crew = Crew(
            agents=[Firstone().researcher()],
            tasks=[Firstone().research_task()],
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disable memory to reduce API calls
            cache=True,  # Enable caching
            max_rpm=10,  # Respect rate limits
        )
        
        try:
            result = research_crew.kickoff(inputs=inputs)
            print("\n📄 Research result received")
            self.state.research_result = result.raw
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"\n⚠️  API Quota Exceeded. Waiting 60 seconds before retry...")
                time.sleep(60)
                # Retry once after waiting
                result = research_crew.kickoff(inputs=inputs)
                print("\n📄 Research result received (after retry)")
                self.state.research_result = result.raw
            else:
                raise e

    @router(generate_research)
    def evaluate_research(self):
        """Evaluate research with reviewer agent"""
        print(f"\n{'='*80}")
        print(f"🔍 EVALUATING RESEARCH (Attempt {self.state.retry_count + 1})")
        print(f"{'='*80}\n")
        
        # Check max retry (reduced to 3 for efficiency)
        if self.state.retry_count >= 3:
            print("\n⚠️  Maximum retry count reached (3 attempts)")
            return "max_retry_exceeded"
        
        # Create review crew (reviewer only)
        from crewai import Crew, Process, Task
        
        # Create a standalone review task with the research result as context
        review_task = Task(
            description=f"""
Review and critically evaluate this research report about {self.state.topic}:

{self.state.research_result}

Follow the strict quality criteria defined in your task configuration.
""",
            expected_output=Firstone().tasks_config['review_task']['expected_output'],
            agent=Firstone().reviewer(),
            output_pydantic=Firstone.ResearchVerification if hasattr(Firstone, 'ResearchVerification') else None
        )
        
        review_crew = Crew(
            agents=[Firstone().reviewer()],
            tasks=[review_task],
            process=Process.sequential,
            verbose=True,
        )
        
        result = review_crew.kickoff(inputs={"topic": self.state.topic})
        
        # Extract validation from pydantic output
        if hasattr(result, 'pydantic') and result.pydantic:
            self.state.valid = result.pydantic.valid
            self.state.feedback = result.pydantic.feedback
        else:
            # Fallback: try to parse from raw output
            import json
            try:
                raw_output = str(result.raw)
                if '{' in raw_output and '}' in raw_output:
                    start = raw_output.index('{')
                    end = raw_output.rindex('}') + 1
                    json_str = raw_output[start:end]
                    review_data = json.loads(json_str)
                    self.state.valid = review_data.get('approved', review_data.get('valid', False))
                    
                    # Build feedback from rejection reasons if present
                    if not self.state.valid:
                        rejection_reasons = review_data.get('rejection_reasons', [])
                        if rejection_reasons:
                            self.state.feedback = "\n".join(f"- {reason}" for reason in rejection_reasons)
                        else:
                            self.state.feedback = review_data.get('feedback', review_data.get('summary', 'Research did not meet quality standards'))
                    else:
                        self.state.feedback = None
            except Exception as e:
                print(f"⚠️  Could not parse review output: {e}")
                self.state.valid = False
                self.state.feedback = "Review parsing failed"
        
        print(f"\n✅ Valid: {self.state.valid}")
        if self.state.feedback:
            print(f"📝 Feedback: {self.state.feedback[:200]}...")
        
        self.state.retry_count += 1
        
        if self.state.valid:
            print("\n✅ Research APPROVED - Proceeding to synthesis")
            return "approved"
        
        print(f"\n❌ Research REJECTED - Retry {self.state.retry_count}/3")
        return "retry"

    @listen("approved")
    def synthesize_result(self):
        """Generate final synthesis report"""
        print(f"\n{'='*80}")
        print(f"📊 GENERATING SYNTHESIS REPORT")
        print(f"{'='*80}\n")
        
        # Create synthesis crew
        from crewai import Crew, Process
        synthesis_crew = Crew(
            agents=[Firstone().synthesizer()],
            tasks=[Firstone().synthesize_task()],
            process=Process.sequential,
            verbose=True,
        )
        
        synthesis_inputs = {
            "topic": self.state.topic,
            "current_year": self.state.current_year,
            "approved_research": self.state.research_result
        }
        
        result = synthesis_crew.kickoff(inputs=synthesis_inputs)
        
        print(f"\n{'='*80}")
        print(f"✅ SYNTHESIS COMPLETE")
        print(f"Total iterations: {self.state.retry_count}")
        print(f"Output saved to: output/synthesis_report.md")
        print(f"{'='*80}\n")

    @listen("max_retry_exceeded")
    def max_retry_exceeded_exit(self):
        """Handle max retry exceeded"""
        print(f"\n{'='*80}")
        print(f"❌ RESEARCH FAILED - MAX RETRIES EXCEEDED")
        print(f"{'='*80}")
        print(f"Total attempts: {self.state.retry_count}")
        print(f"The research could not meet quality criteria after 3 attempts.")
        print(f"Last feedback: {self.state.feedback}")
        print(f"{'='*80}\n")
        
        # Save failed research to file
        with open("output/failed_research.md", "w") as file:
            file.write(f"# Failed Research Report\n\n")
            file.write(f"**Topic:** {self.state.topic}\n\n")
            file.write(f"**Attempts:** {self.state.retry_count}\n\n")
            file.write(f"## Last Research Output\n\n{self.state.research_result}\n\n")
            file.write(f"## Last Reviewer Feedback\n\n{self.state.feedback}\n")


def run():
    """
    Run the research flow with iterative research-review loop.
    """
    # Check for API keys
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY or GEMINI_API_KEY not found in .env file")
        print("Please add your API key to the .env file")
        return
    
    if not os.getenv("SERPER_API_KEY"):
        print("⚠️  WARNING: SERPER_API_KEY not found in .env file")
        print("Web search functionality may be limited")
    
    print(f"\n{'='*80}")
    print(f"🚀 STARTING RESEARCH FLOW")
    print(f"{'='*80}")
    print(f"⚙️  Configuration:")
    print(f"  - Max iterations: 3 (reduced for efficiency)")
    print(f"  - Rate limit: 10 requests/minute")
    print(f"  - Retry delay: 10 seconds")
    print(f"  - API quota retry: 60 seconds")
    print(f"  - Review criteria: Balanced (not overly strict)")
    print(f"{'='*80}\n")
    
    # Initialize flow
    research_flow = ResearchFlow()
    
    # Set initial state
    research_flow.state.topic = "The rise of cristiano ronaldo and his impact on modern football"
    research_flow.state.current_year = str(datetime.now().year)
    
    # Kickoff the flow
    try:
        research_flow.kickoff()
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print(f"\n{'='*80}")
            print(f"⚠️  API QUOTA EXCEEDED")
            print(f"{'='*80}")
            print(f"The Gemini API free tier has a limit of 10 requests per minute.")
            print(f"Please wait 1-2 minutes and try again.")
            print(f"{'='*80}\n")
        else:
            raise e


def plot():
    """
    Plot the research flow diagram.
    """
    research_flow = ResearchFlow()
    research_flow.plot()


if __name__ == "__main__":
    run()
