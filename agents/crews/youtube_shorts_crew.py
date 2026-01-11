"""YouTube Shorts Creation Crew

CrewAI crew configuration for automated YouTube shorts creation
from long-form video content.
"""

from crewai import Crew, Agent, Task, Process
from agents.video_editing_agent import VideoEditingAgent
from agents.transcription_agent import TranscriptionAgent
from agents.funny_moment_agent import FunnyMomentAgent


class YouTubeShortsCrew:
    """CrewAI crew for YouTube shorts creation."""

    def __init__(self):
        """Initialize the crew with agents and tasks."""
        self.video_editor = self._create_video_editor_agent()
        self.transcriptionist = self._create_transcription_agent()
        self.funny_moment_detector = self._create_funny_moment_agent()

    def _create_video_editor_agent(self) -> Agent:
        """Create video editor agent."""
        return Agent(
            role="Video Editor",
            goal="Download and prepare video content for analysis",
            backstory="""
                You are a skilled video editor with expertise in downloading
                and preparing YouTube videos for content analysis.
            """,
            verbose=True,
            allow_delegation=False,
            tools=[
                VideoEditingAgent().get_tool("download_video"),
                VideoEditingAgent().get_tool("extract_audio"),
                VideoEditingAgent().get_tool("trim_video"),
            ]
        )

    def _create_transcription_agent(self) -> Agent:
        """Create transcription agent."""
        return Agent(
            role="Transcription Specialist",
            goal="Convert video audio to text for content analysis",
            backstory="""
                You are an expert in speech-to-text conversion with
                specialized knowledge in podcast and comedy content transcription.
            """,
            verbose=True,
            allow_delegation=False,
            tools=[
                TranscriptionAgent().get_tool("transcribe_audio"),
            ]
        )

    def _create_funny_moment_agent(self) -> Agent:
        """Create funny moment detection agent."""
        return Agent(
            role="Comedy Content Analyst",
            goal="Identify and extract funny moments from video content",
            backstory="""
                You are a comedy expert with years of experience analyzing
                humorous content. You can spot funny moments, jokes, and
                comedic timing in video transcripts and audio.
            """,
            verbose=True,
            allow_delegation=False,
            tools=[
                FunnyMomentAgent().get_tool("analyze_transcript"),
                FunnyMomentAgent().get_tool("detect_laughter"),
                FunnyMomentAgent().get_tool("identify_funny_clips"),
            ]
        )

    def create_download_task(self, youtube_url: str, output_path: str) -> Task:
        """Create video download task."""
        return Task(
            description=f"""
                Download the YouTube video from {youtube_url}
                and save it to {output_path} with the best available quality.
                Ensure the video is properly formatted for further processing.
            """,
            agent=self.video_editor,
            expected_output="Downloaded video file with metadata including title, duration, and file size."
        )

    def create_transcription_task(self, video_path: str, output_dir: str) -> Task:
        """Create video transcription task."""
        return Task(
            description=f"""
                Extract audio from the video at {video_path}
                and create a detailed transcript with timestamps.
                Save the transcript files to {output_dir}.
            """,
            agent=self.transcriptionist,
            expected_output="Complete transcript in VTT and JSON formats with accurate timestamps."
        )

    def create_funny_moment_analysis_task(self, transcript_path: str) -> Task:
        """Create funny moment analysis task."""
        return Task(
            description=f"""
                Analyze the transcript at {transcript_path}
                to identify funny moments, jokes, and comedic segments.
                Focus on segments that would work well for YouTube Shorts.
            """,
            agent=self.funny_moment_detector,
            expected_output="List of funny segments with timestamps, funny scores, and context."
        )

    def create_clip_creation_task(self, video_path: str, transcript_path: str,
                                 output_dir: str, funny_segments: list) -> Task:
        """Create funny clip creation task."""
        return Task(
            description=f"""
                Using the funny segments analysis, create actual video clips
                from {video_path} based on the transcript at {transcript_path}.
                Save the clips to {output_dir} with appropriate naming.

                Funny segments to process: {len(funny_segments)} segments
            """,
            agent=self.funny_moment_detector,
            expected_output="Multiple video clips ready for YouTube Shorts upload, with metadata file."
        )

    def run_crew(self, youtube_url: str, output_dir: str = "youtube_shorts_crew") -> dict:
        """Run the complete YouTube shorts creation crew."""

        # Create tasks
        download_task = self.create_download_task(
            youtube_url,
            f"{output_dir}/original_video.mp4"
        )

        transcription_task = self.create_transcription_task(
            f"{output_dir}/original_video.mp4",
            output_dir
        )

        funny_analysis_task = self.create_funny_moment_analysis_task(
            f"{output_dir}/transcript.vtt"
        )

        clip_creation_task = self.create_clip_creation_task(
            f"{output_dir}/original_video.mp4",
            f"{output_dir}/transcript.vtt",
            f"{output_dir}/clips",
            []  # This would be populated with actual segments in runtime
        )

        # Create crew
        crew = Crew(
            agents=[
                self.video_editor,
                self.transcriptionist,
                self.funny_moment_detector
            ],
            tasks=[
                download_task,
                transcription_task,
                funny_analysis_task,
                clip_creation_task
            ],
            process=Process.sequential,
            verbose=2
        )

        # Execute crew
        result = crew.kickoff()

        return {
            "status": "completed",
            "youtube_url": youtube_url,
            "output_dir": output_dir,
            "result": result,
            "crew_process": "sequential"
        }


def create_youtube_shorts_crew() -> YouTubeShortsCrew:
    """Factory function to create YouTube shorts crew."""
    return YouTubeShortsCrew()


if __name__ == "__main__":
    # Example usage
    crew = create_youtube_shorts_crew()

    # Example YouTube URL (would be replaced with actual URL)
    example_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    print(f"Running YouTube Shorts Crew for: {example_url}")
    result = crew.run_crew(example_url)

    print(f"Crew completed! Results saved to: {result['output_dir']}")
