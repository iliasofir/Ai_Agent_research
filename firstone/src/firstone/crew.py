from typing import List, Optional
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import ArxivPaperTool
from crewai_tools import FileWriterTool
from pydantic import BaseModel, Field
from .tools.pdf_reader_tool import read_pdf


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# Pydantic model for review validation output
class ResearchVerification(BaseModel):
    """Structured output for review validation"""
    valid: bool = Field(
        description="True if research meets quality criteria and should proceed to synthesis, False otherwise"
    )
    feedback: Optional[str] = Field(
        default=None,
        description="Detailed feedback if research is rejected, None if approved"
    )


arxiv = ArxivPaperTool(
    download_pdfs=False,
    save_dir="./arxiv_pdfs",
    use_title_as_filename=True,
)


@CrewBase
class Firstone():
    """Firstone crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    # Export ResearchVerification for use in Flow
    ResearchVerification = ResearchVerification


    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=False,
            tools=[SerperDevTool(), arxiv, read_pdf],  # Adding the SerperDevTool and ArxivPaperTool to the agent's tools
            max_iter=15,  # Limit iterations to prevent excessive API calls
            max_rpm=10,  # Limit requests per minute
        )

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['reviewer'], # type: ignore[index]
            verbose=True
        )
    

    @agent
    def synthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['synthesizer'], # type: ignore[index]
            verbose=False
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
            
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'], # type: ignore[index]
            output_pydantic=ResearchVerification,
            context=[self.research_task()]
        )
    

    @task
    def synthesize_task(self) -> Task:
        return Task(
            config=self.tasks_config['synthesis_task'], # type: ignore[index]
            context=[self.research_task(), self.review_task()],
            output_file='output/synthesis_report.md',
        )

    @crew
    def crew(self) -> Crew:
        """Creates the research crew with conditional synthesis logic"""
        # Define all tasks
        research = self.research_task()
        review = self.review_task()
        synthesis = self.synthesize_task()
        
        # Create the crew with tasks in sequential order
        # The synthesizer will check review approval in its task description
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=[research, review, synthesis], # Sequential execution
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disable memory to reduce API calls
            cache=True,  # Enable caching to reuse responses
            max_rpm=10,  # Limit requests per minute to respect quota
        )
