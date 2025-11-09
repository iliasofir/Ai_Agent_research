"""
Routes de recherche avec WebSocket progress tracking
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import time
import asyncio
from threading import Thread
from pathlib import Path
import shutil


from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from crewai.flow.flow import router as flow_router

from app.models.schemas import (
    ResearchRequest,
    ResearchResponse,
    ResearchResult,
    ResearchStatus
)
from app.websocket_manager import manager
from firstone.crew import Firstone

router = APIRouter()



# Create uploads directory
UPLOAD_DIR = Path("uploads/pdfs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class ResearchFlowState(BaseModel):
    """State model for the research flow"""
    topic: str = ""
    current_year: str = ""
    research_result: str = ""
    feedback: Optional[str] = None
    valid: bool = False
    retry_count: int = 0
    pdf_paths: List[str] = []  # List of PDF file paths to analyze
    pdf_content: str = ""  # Ext


class ResearchFlow(Flow[ResearchFlowState]):
    """Flow for iterative research-review-synthesis workflow with WebSocket progress"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws_manager = manager  # Reference to global WebSocket manager

    def send_ws_update(self, agent: str, status: str, message: str = "", 
                       details: Dict = None, iteration: int = None):
        """Synchronous wrapper to send WebSocket updates from sync flow"""
        try:
            # Create new event loop for this thread if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async broadcast in the loop
            if loop.is_running():
                # If loop is already running, create task
                asyncio.create_task(
                    self.ws_manager.broadcast(agent, status, message, details, iteration)
                )
            else:
                # If loop is not running, run until complete
                loop.run_until_complete(
                    self.ws_manager.broadcast(agent, status, message, details, iteration)
                )
        except Exception as e:
            print(f"⚠️ WebSocket update failed: {e}")

    @start("retry")
    def generate_research(self):
        """Generate research with researcher agent"""
        iteration = self.state.retry_count + 1
        
        # Notify research start
        self.send_ws_update(
            agent="Researcher",
            status="thinking" if iteration == 1 else "retry",
            message=f"Starting research iteration {iteration}...",
            iteration=iteration
        )
        
        print(f"\n{'='*80}")
        print(f"📚 ITERATION {iteration} - Running Research Task")
        print(f"{'='*80}\n")
        
        # Delay between retries
        if self.state.retry_count > 0:
            delay = 10
            self.send_ws_update(
                agent="Researcher",
                status="thinking",
                message=f"Waiting {delay}s before retry (API rate limit)...",
                iteration=iteration
            )
            print(f"⏱️  Waiting {delay} seconds before retry...")
            time.sleep(delay)
        
        # Prepare inputs
        inputs = {
            "topic": self.state.topic,
            "current_year": self.state.current_year
        }

        # Add PDF content if available
        if self.state.pdf_content:
            inputs["uploaded_pdfs"] = f"""
📚 UPLOADED PDF DOCUMENTS (USE AS PRIMARY SOURCES):

{self.state.pdf_content}

IMPORTANT INSTRUCTIONS FOR USING UPLOADED PDFs:
- These PDFs are the PRIMARY sources for your research
- Extract key findings, methodologies, and citations from these documents
- Reference these documents prominently in your research
- Supplement with additional papers from ArXiv/Web only if necessary
- Make sure to cite the uploaded PDFs in your report
"""
            print(f"\n📄 Using {len(self.state.pdf_paths)} uploaded PDF(s) as primary sources")
        
        
        if self.state.feedback:
            self.send_ws_update(
                agent="Researcher",
                status="working",
                message=f"Addressing reviewer feedback (attempt {iteration}/3)...",
                iteration=iteration
            )
            inputs["feedback"] = f"""
PREVIOUS ATTEMPT WAS REJECTED (Attempt {self.state.retry_count}).

REVIEWER FEEDBACK:
{self.state.feedback}

FOCUS ON IMPROVEMENTS:
- Address specific issues from feedback
- Ensure 5-7 high-quality papers
- Provide clear explanations (50+ words each)
- Use credible sources (ArXiv, peer-reviewed)

This is attempt {iteration} of 3. Make it count!
"""
        else:
            self.send_ws_update(
                agent="Researcher",
                status="working",
                message="Gathering information from web and ArXiv papers...",
                iteration=iteration
            )
        
        # Create research crew
        from crewai import Crew, Process
        research_crew = Crew(
            agents=[Firstone().researcher()],
            tasks=[Firstone().research_task()],
            process=Process.sequential,
            verbose=True,
            memory=False,
            cache=True,
            max_rpm=10,
        )
        
        try:
            result = research_crew.kickoff(inputs=inputs)
            print("\n📄 Research result received")
            self.state.research_result = result.raw
            
            # Notify research completion
            self.send_ws_update(
                agent="Researcher",
                status="done",
                message=f"Research completed ({len(result.raw)} chars)",
                iteration=iteration,
                details={"output_length": len(result.raw)}
            )
            
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                self.send_ws_update(
                    agent="Researcher",
                    status="retry",
                    message="API quota exceeded, waiting 60s...",
                    iteration=iteration
                )
                print(f"\n⚠️  API Quota Exceeded. Waiting 60 seconds...")
                time.sleep(60)
                result = research_crew.kickoff(inputs=inputs)
                self.state.research_result = result.raw
            else:
                self.send_ws_update(
                    agent="Researcher",
                    status="error",
                    message=f"Error: {str(e)}",
                    iteration=iteration
                )
                raise e

    @flow_router(generate_research)
    def evaluate_research(self):
        """Evaluate research with reviewer agent"""
        iteration = self.state.retry_count + 1
        
        # Notify review start
        self.send_ws_update(
            agent="Reviewer",
            status="thinking",
            message=f"Evaluating research quality (attempt {iteration})...",
            iteration=iteration
        )
        
        print(f"\n{'='*80}")
        print(f"🔍 EVALUATING RESEARCH (Attempt {iteration})")
        print(f"{'='*80}\n")
        
        # Check max retry
        if self.state.retry_count >= 3:
            self.send_ws_update(
                agent="Reviewer",
                status="error",
                message="Maximum retry limit reached (3 attempts)",
                iteration=iteration
            )
            print("\n⚠️  Maximum retry count reached")
            return "max_retry_exceeded"
        
        self.send_ws_update(
            agent="Reviewer",
            status="working",
            message="Analyzing research papers and validating quality...",
            iteration=iteration
        )
        
        # Create review crew
        from crewai import Crew, Process, Task
        
        review_task = Task(
            description=f"""
Review and critically evaluate this research report about {self.state.topic}:

{self.state.research_result}

Follow the balanced quality criteria defined in your task configuration.
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
        
        # Extract validation
        if hasattr(result, 'pydantic') and result.pydantic:
            self.state.valid = result.pydantic.valid
            self.state.feedback = result.pydantic.feedback
        else:
            # Fallback parsing
            import json
            try:
                raw_output = str(result.raw)
                if '{' in raw_output and '}' in raw_output:
                    start = raw_output.index('{')
                    end = raw_output.rindex('}') + 1
                    json_str = raw_output[start:end]
                    review_data = json.loads(json_str)
                    self.state.valid = review_data.get('approved', review_data.get('valid', False))
                    
                    if not self.state.valid:
                        rejection_reasons = review_data.get('rejection_reasons', [])
                        if rejection_reasons:
                            self.state.feedback = "\n".join(f"- {reason}" for reason in rejection_reasons)
                        else:
                            self.state.feedback = review_data.get('feedback', 'Did not meet quality standards')
                    else:
                        self.state.feedback = None
            except Exception as e:
                print(f"⚠️  Could not parse review output: {e}")
                self.state.valid = False
                self.state.feedback = "Review parsing failed"
        
        self.state.retry_count += 1
        
        if self.state.valid:
            self.send_ws_update(
                agent="Reviewer",
                status="done",
                message="✓ Research approved! Proceeding to synthesis...",
                iteration=iteration,
                details={"approved": True}
            )
            print("\n✅ Research APPROVED")
            return "approved"
        
        self.send_ws_update(
            agent="Reviewer",
            status="retry",
            message=f"✗ Research rejected. Retry {self.state.retry_count}/3",
            iteration=iteration,
            details={
                "approved": False,
                "feedback": self.state.feedback[:200] if self.state.feedback else ""
            }
        )
        print(f"\n❌ Research REJECTED - Retry {self.state.retry_count}/3")
        return "retry"

    @listen("approved")
    def synthesize_result(self):
        """Generate final synthesis report"""
        self.send_ws_update(
            agent="Synthesizer",
            status="thinking",
            message="Starting synthesis report generation...",
            details={"iterations_required": self.state.retry_count}
        )
        
        print(f"\n{'='*80}")
        print(f"📊 GENERATING SYNTHESIS REPORT")
        print(f"{'='*80}\n")
        
        self.send_ws_update(
            agent="Synthesizer",
            status="working",
            message="Analyzing patterns and synthesizing findings...",
        )
        
        # Create synthesis crew
        from crewai import Crew, Process, Task
        
        synthesis_task = Task(
            description=f"""
Create a comprehensive synthesis report on {self.state.topic} using the approved research papers below.

APPROVED RESEARCH PAPERS:
{self.state.research_result}

REVIEW STATUS: APPROVED after {self.state.retry_count} iteration(s)

Your tasks:
1. Extract key themes and patterns across papers
2. Identify consensus and disagreement areas
3. Synthesize insights into cohesive narrative
4. Provide actionable recommendations

Include: Executive Summary, Introduction, Main Findings, Analysis, Conclusions, References
""",
            expected_output="""Comprehensive markdown synthesis report (2000-4000 words) without code blocks.""",
            agent=Firstone().synthesizer(),
            output_file='output/synthesis_report.md'
        )
        
        synthesis_crew = Crew(
            agents=[Firstone().synthesizer()],
            tasks=[synthesis_task],
            process=Process.sequential,
            verbose=True,
        )
        
        synthesis_inputs = {
            "topic": self.state.topic,
            "current_year": self.state.current_year,
        }
        
        result = synthesis_crew.kickoff(inputs=synthesis_inputs)
        
        # Lire le rapport généré
        report_content = ""
        try:
            with open("output/synthesis_report.md", "r", encoding="utf-8") as f:
                report_content = f.read()
        except Exception as e:
            print(f"⚠️ Could not read synthesis report: {e}")
            report_content = str(result.raw) if result else "Report generation failed"
        
        self.send_ws_update(
            agent="Synthesizer",
            status="done",
            message=f"✓ Synthesis complete! Report saved to output/synthesis_report.md",
            details={
                "total_iterations": self.state.retry_count,
                "output_file": "output/synthesis_report.md",
                "report_content": report_content
            }
        )
        
        # Notify overall completion with report
        self.send_ws_update(
            agent="System",
            status="completed",
            message=f"✓ All tasks completed successfully after {self.state.retry_count} iteration(s)!",
            details={
                "total_iterations": self.state.retry_count,
                "final_report": report_content
            }
        )
        
        print(f"\n{'='*80}")
        print(f"✅ SYNTHESIS COMPLETE")
        print(f"Total iterations: {self.state.retry_count}")
        print(f"{'='*80}\n")

    @listen("max_retry_exceeded")
    def max_retry_exceeded_exit(self):
        """Handle max retry exceeded"""
        self.send_ws_update(
            agent="System",
            status="error",
            message=f"✗ Research failed after 3 attempts. Last feedback: {self.state.feedback[:100] if self.state.feedback else ''}...",
            details={
                "total_attempts": self.state.retry_count,
                "last_feedback": self.state.feedback
            }
        )
        
        print(f"\n{'='*80}")
        print(f"❌ RESEARCH FAILED - MAX RETRIES EXCEEDED")
        print(f"{'='*80}\n")
        
        # Save failed research
        with open("output/failed_research.md", "w") as file:
            file.write(f"# Failed Research Report\n\n")
            file.write(f"**Topic:** {self.state.topic}\n\n")
            file.write(f"**Attempts:** {self.state.retry_count}\n\n")
            file.write(f"## Last Research Output\n\n{self.state.research_result}\n\n")
            file.write(f"## Last Reviewer Feedback\n\n{self.state.feedback}\n")


def run_flow_sync(topic: str):
    """Synchronous wrapper to run the flow"""
    try:
        # Send initial update
        asyncio.run(manager.broadcast(
            agent="System",
            status="started",
            message=f"Starting research flow for: {topic}"
        ))
        
        # Initialize and run flow
        research_flow = ResearchFlow()
        research_flow.state.topic = topic
        research_flow.state.current_year = str(datetime.now().year)
        
        # Run flow synchronously (CrewAI flows are sync)
        research_flow.kickoff()
        
    except Exception as e:
        asyncio.run(manager.broadcast(
            agent="System",
            status="error",
            message=f"Flow execution error: {str(e)}"
        ))
        raise


@router.post("/send", response_model=ResearchResponse)
async def create_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Start new research with Flow and real-time WebSocket progress tracking
    """
    topic = request.topic
    
    # Use a separate thread for the synchronous flow
    def run_in_thread():
        run_flow_sync(topic)
    
    # Add thread execution to background tasks
    background_tasks.add_task(lambda: Thread(target=run_in_thread).start())
    
    return ResearchResponse(
        status=ResearchStatus.PENDING,
        topic=topic,
        result="",
        message=f"Research started for '{topic}'. Connect to ws://localhost:8000/api/ws/progress for real-time updates."
    )





@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    topic: Optional[str] = None
):
    """
    Upload a PDF file for research context.
    
    Args:
        file: PDF file to upload
        topic: Optional research topic (if not provided, will extract from PDF)
        
    Returns:
        Upload confirmation with file_id
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Seuls les fichiers PDF sont supportés"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
        
        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract basic info from PDF
        page_count = 0
        extracted_topic = topic
        
        try:
            import PyPDF2
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                page_count = len(pdf_reader.pages)
                
                # Extract first page text for topic detection if not provided
                if not extracted_topic and page_count > 0:
                    first_page = pdf_reader.pages[0].extract_text()
                    # Simple topic extraction (first 100 chars)
                    if first_page:
                        extracted_topic = first_page[:100].strip().replace('\n', ' ')
                    else:
                        extracted_topic = file.filename.replace('.pdf', '')
        except:
            if not extracted_topic:
                extracted_topic = file.filename.replace('.pdf', '')
        
        return {
            "status": "success",
            "message": f"PDF uploadé avec succès: {file.filename}",
            "file_id": file_id,
            "file_path": str(file_path),
            "filename": file.filename,
            "topic": extracted_topic,
            "page_count": page_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'upload du PDF: {str(e)}"
        )


@router.post("/send-with-pdfs", response_model=ResearchResponse)
async def send_research_with_pdfs(
    topic: str,
    file_ids: Optional[List[str]] = None
):
    """
    Send a research request with optional PDF files as context.
    
    Args:
        topic: Research topic
        file_ids: List of file IDs from previous uploads
        
    Returns:
        Research response
    """
    try:
        # Prepare PDF paths if provided
        pdf_paths = []
        if file_ids:
            for file_id in file_ids:
                pdf_path = UPLOAD_DIR / f"{file_id}.pdf"
                if pdf_path.exists():
                    pdf_paths.append(str(pdf_path))
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"PDF avec file_id {file_id} non trouvé"
                    )
        
        # Create and initialize the research flow
        research_flow = ResearchFlow()
        research_flow.state.topic = topic
        research_flow.state.current_year = str(datetime.now().year)
        research_flow.state.pdf_paths = pdf_paths
        
        # Extract PDF content if provided
        if pdf_paths:
            print(f"\n📚 Extraction du contenu de {len(pdf_paths)} PDF(s)...")
            from firstone.tools.pdf_reader_tool import PDFReaderTool
            pdf_tool = PDFReaderTool()
            
            pdf_contents = []
            for pdf_path in pdf_paths:
                print(f"  - Extraction de {Path(pdf_path).name}...")
                content = pdf_tool._run(pdf_path=pdf_path, max_pages=20)  # Limit to 20 pages per PDF
                pdf_contents.append(f"\n{'='*80}\nFichier: {Path(pdf_path).name}\n{'='*80}\n{content}")
            
            research_flow.state.pdf_content = "\n\n".join(pdf_contents)
            print(f"✅ Contenu extrait de {len(pdf_paths)} PDF(s)")
        
        # Kickoff the flow asynchronously
        await research_flow.kickoff_async()
        
        # Get the final result from the state
        if research_flow.state.valid:
            # Research was approved and synthesis completed
            # Read the synthesis report from file
            try:
                with open("output/synthesis_report.md", "r") as f:
                    result = f.read()
            except FileNotFoundError:
                result = research_flow.state.research_result
            
            pdf_info = f" avec {len(pdf_paths)} PDF(s)" if pdf_paths else ""
            
            return ResearchResponse(
                status=ResearchStatus.COMPLETED,
                topic=topic,
                result=result,
                message=f"Recherche '{topic}'{pdf_info} terminée avec succès après {research_flow.state.retry_count} itération(s)"
            )
        else:
            # Research failed after max retries
            return ResearchResponse(
                status=ResearchStatus.FAILED,
                topic=topic,
                result=f"Research failed after {research_flow.state.retry_count} attempts.\n\nLast feedback:\n{research_flow.state.feedback}",
                message=f"Recherche '{topic}' échouée après {research_flow.state.retry_count} tentatives"
            )
    
    except Exception as e:
        error_msg = str(e)
        
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return ResearchResponse(
                status=ResearchStatus.FAILED,
                topic=topic,
                result="",
                message="API quota dépassé. Veuillez réessayer dans 1-2 minutes."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'exécution de la recherche: {error_msg}"
            )



@router.get("/status")
async def get_status():
    """Get current system status"""
    return {
        "active_connections": len(manager.active_connections),
        "status": "operational"
    }