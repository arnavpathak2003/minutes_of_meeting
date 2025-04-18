#!/usr/bin/env python

from pydantic import BaseModel
from pydub.utils import make_chunks
from pydub import AudioSegment
from crewai.flow import Flow, listen, start
from pathlib import Path
import whisper
from crews.minutes_of_meeting.minutes_of_meeting_crew import (
    MeetingMinutesCrew,
)
from crews.send_email.send_email import SendEmail


class MeetingMinutesState(BaseModel):
    transcript: str = ""
    minutes: str = ""


class MeetingMinutesFlow(Flow[MeetingMinutesState]):
    @start()
    def transcribe_meeting(self):
        print("Generating meeting minutes...")

        try:
            audio_path = Path("EarningsCall.wav")
            transcript_dir = Path("transcripts")
            temp_dir = Path("temp_chunks")

            transcript_dir.mkdir(exist_ok=True)
            temp_dir.mkdir(exist_ok=True)

            audio = AudioSegment.from_file(audio_path, format="wav")
            chunks = make_chunks(audio, 60000)
            model = whisper.load_model("tiny")

            full_transcript = ""
            chunk_files = []

            try:
                for i, chunk in enumerate(chunks):
                    chunk_path = temp_dir / f"chunk_{i}.wav"
                    chunk_files.append(chunk_path)
                    chunk.export(chunk_path, format="wav")

                for chunk_path in chunk_files:
                    result = model.transcribe(str(chunk_path))
                    full_transcript += result["text"] + " "

            finally:
                for chunk_path in chunk_files:
                    if chunk_path.exists():
                        chunk_path.unlink()
                if temp_dir.exists():
                    temp_dir.rmdir()

            self.state.transcript = full_transcript.strip()

            transcript_path = transcript_dir / f"transcript_{audio_path.stem}.txt"
            transcript_path.write_text(self.state.transcript)

            print(f"Transcription completed and saved to {transcript_path}")

        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            raise

    @listen(transcribe_meeting)
    def generate_minutes(self):
        print("Generating minutes...")

        company_name = input("Enter your company name: ")
        organizer_name = input("Enter organizer name: ")

        crew = MeetingMinutesCrew()
        crew.inputs = {
            "transcript": self.state.transcript,
            "company_name": company_name,
            "organizer_name": organizer_name,
        }

        inputs = {
            "transcript": self.state.transcript,
            "company_name": company_name,
            "organizer_name": organizer_name,
        }
        minutes = crew.crew().kickoff(inputs)
        self.state.minutes = minutes

    @listen(generate_minutes)
    def create_draft_meeting_minutes(self):
        print("Creating draft meeting minutes...")

        crew = SendEmail()
        inputs = {
            "body": str(self.state.minutes),
        }

        send_crew = crew.crew().kickoff(inputs)
        print(f"Draft Crew : {send_crew}")


def kickoff():
    meeting_minutes_flow = MeetingMinutesFlow()
    meeting_minutes_flow.plot()
    meeting_minutes_flow.kickoff()


if __name__ == "__main__":
    kickoff()
