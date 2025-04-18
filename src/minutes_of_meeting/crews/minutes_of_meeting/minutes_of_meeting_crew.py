from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileWriterTool
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

file_writer_tool_summary = FileWriterTool(
    filename="summary.txt", directory="meeting_minutes"
)
file_writer_tool_action_items = FileWriterTool(
    filename="action_items.txt", directory="meeting_minutes"
)
file_writer_tool_sentiment = FileWriterTool(
    filename="sentiment.txt", directory="meeting_minutes"
)


@CrewBase
class MeetingMinutesCrew:
    """Meeting Minutes Crew"""

    def __init__(self):
        meeting_minutes_dir = Path("meeting_minutes")

        if meeting_minutes_dir.exists():
            shutil.rmtree(meeting_minutes_dir)

        meeting_minutes_dir.mkdir(parents=True, exist_ok=True)

        self.inputs = {}

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    llm = LLM(model="ollama/phi4", api_base="http://localhost:11434")

    @agent
    def meeting_minutes_summarizer(self) -> Agent:
        return Agent(
            config=self.agents_config["meeting_minutes_summarizer"],
            tools=[
                file_writer_tool_summary,
                file_writer_tool_action_items,
                file_writer_tool_sentiment,
            ],
            llm=self.llm,
        )

    @agent
    def meeting_minutes_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["meeting_minutes_writer"],
            # llm=self.llm,
        )

    @task
    def meeting_minutes_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["meeting_minutes_summary_task"],
        )

    @task
    def meeting_minutes_writing_task(self) -> Task:
        task_config = dict(self.tasks_config["meeting_minutes_writing_task"])
        if "company_name" in self.inputs and "organizer_name" in self.inputs:
            description = task_config["description"].format(
                company_name=self.inputs.get("company_name", "Company"),
                organizer_name=self.inputs.get("organizer_name", "Organizer"),
            )
            task_config["description"] = description

        return Task(
            config=task_config,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            inputs=self.inputs,
        )
