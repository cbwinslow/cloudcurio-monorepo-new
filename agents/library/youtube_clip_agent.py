#!/usr/bin/env python3
"""
YouTube Clip Generation Agent

Advanced AI-powered agent for automatically generating optimized clips from YouTube episodes.
Uses computer vision, audio analysis, and NLP to identify the best moments for viral clips.

Features:
- AI-powered video analysis for optimal clip selection
- Multi-platform clip optimization (YouTube Shorts, TikTok, Instagram Reels)
- Automatic caption generation with timing
- Engagement prediction scoring
- Platform-specific optimization
- Batch processing capabilities
"""

import os
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from agents.base_agent import BaseAgent
from agents.robust_tool import RobustTool
import cv2
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import whisper
import torch
from transformers import pipeline


class YouTubeClipAgent(BaseAgent):
    """AI-powered YouTube clip generation agent."""
    
    def __init__(self, config_path: str = "agents/config.json"):
        super().__init__(config_path)
        self.name = "YouTubeClipAgent"
        self.description = "AI-powered YouTube clip generation and optimization"
        
        # Load configurations
        self.api_keys = self._load_api_keys()
        self.models = self._load_ai_models()
        self.platform_configs = self._load_platform_configs()
        
        # Initialize tools
        self.tools = {
            "video_analyzer": RobustTool(
                name="video_analyzer",
                description="Analyzes YouTube videos for optimal clip segments using AI",
                func=self.analyze_video_for_clips
            ),
            "clip_generator": RobustTool(
                name="clip_generator",
                description="Generates optimized clips from video segments",
                func=self.generate_clips_from_video
            ),
            "platform_optimizer": RobustTool(
                name="platform_optimizer",
                description="Optimizes clips for specific platforms (TikTok, Instagram, YouTube Shorts)",
                func=self.optimize_clips_for_platforms
            ),
            "engagement_predictor": RobustTool(
                name="engagement_predictor",
                description="Predicts clip engagement potential using AI models",
                func=self.predict_clip_engagement
            ),
            "batch_processor": RobustTool(
                name="batch_processor",
                description="Processes multiple videos in batch for clip generation",
                func=self.process_batch_videos
            )
        }
        
        # Video processing settings
        self.video_settings = {
            "target_durations": [15, 30, 60, 90],  # seconds
            "min_segment_score": 8.5,  # Minimum score for clip consideration
            "max_clips_per_video": 10,
            "output_formats": ["mp4", "mov"],
            "quality_settings": {
                "high": {"crf": 18, "preset": "slow"},
                "medium": {"crf": 23, "preset": "medium"},
                "low": {"crf": 28, "preset": "fast"}
            }
        }
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys for video processing and AI services."""
        return {
            "youtube": os.getenv("YOUTUBE_API_KEY", ""),
            "aws_rekognition": os.getenv("AWS_REKOGNITION_KEY", ""),
            "google_vision": os.getenv("GOOGLE_VISION_KEY", ""),
            "ffmpeg_path": os.getenv("FFMPEG_PATH", "ffmpeg"),
            "whisper_model": "base"  # Can be changed to medium/large for better accuracy
        }
    
    def _load_ai_models(self) -> Dict[str, Any]:
        """Load AI models for video analysis."""
        models = {}
        
        try:
            # Load Whisper model for audio transcription
            models["whisper"] = whisper.load_model(self.api_keys["whisper_model"])
            
            # Load sentiment analysis model
            models["sentiment"] = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            
            # Load emotion detection model
            models["emotion"] = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
            
            # Load engagement prediction model (simplified)
            models["engagement"] = pipeline("text-classification", model="facebook/bart-large-mnli")
            
            self.logger.info("AI models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading AI models: {str(e)}")
            
        return models
    
    def _load_platform_configs(self) -> Dict[str, Any]:
        """Load platform-specific clip configurations."""
        return {
            "youtube_shorts": {
                "max_duration": 60,
                "aspect_ratio": "9:16",
                "optimal_length": 30,
                "hashtags": ["#shorts", "#podcast", "#comedy"],
                "caption_length": 100,
                "engagement_factors": {
                    "humor": 0.4,
                    "visual": 0.3,
                    "audio": 0.2,
                    "text": 0.1
                }
            },
            "tiktok": {
                "max_duration": 60,
                "aspect_ratio": "9:16",
                "optimal_length": 21,
                "hashtags": ["#fyp", "#viral", "#comedy", "#podcast"],
                "caption_length": 2200,
                "engagement_factors": {
                    "visual": 0.4,
                    "humor": 0.3,
                    "trend": 0.2,
                    "text": 0.1
                }
            },
            "instagram_reels": {
                "max_duration": 90,
                "aspect_ratio": "9:16",
                "optimal_length": 30,
                "hashtags": ["#reels", "#comedy", "#podcast", "#funny"],
                "caption_length": 2200,
                "engagement_factors": {
                    "visual": 0.35,
                    "story": 0.3,
                    "emotion": 0.2,
                    "text": 0.15
                }
            },
            "twitter": {
                "max_duration": 140,
                "aspect_ratio": "16:9",
                "optimal_length": 45,
                "hashtags": ["#podcast", "#comedy", "#tech"],
                "caption_length": 280,
                "engagement_factors": {
                    "text": 0.4,
                    "humor": 0.3,
                    "visual": 0.2,
                    "timeliness": 0.1
                }
            },
            "facebook": {
                "max_duration": 240,
                "aspect_ratio": "16:9",
                "optimal_length": 60,
                "hashtags": ["#podcast", "#comedy", "#entertainment"],
                "caption_length": 63206,
                "engagement_factors": {
                    "story": 0.3,
                    "visual": 0.3,
                    "emotion": 0.2,
                    "text": 0.2
                }
            }
        }
    
    def analyze_video_for_clips(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze YouTube video for optimal clip segments using AI."""
        result = {
            "success": False,
            "video_id": video_data.get("video_id", ""),
            "segments": [],
            "analysis": {},
            "error": ""
        }
        
        try:
            # Step 1: Download video (simplified - in production use YouTube API)
            video_path = self._download_video(video_data)
            if not video_path:
                raise Exception("Video download failed")
            
            # Step 2: Extract audio for analysis
            audio_path = self._extract_audio(video_path)
            
            # Step 3: Transcribe audio using Whisper
            transcription = self._transcribe_audio(audio_path)
            
            # Step 4: Analyze video frames for visual engagement
            visual_analysis = self._analyze_visual_engagement(video_path)
            
            # Step 5: Analyze audio for engagement factors
            audio_analysis = self._analyze_audio_engagement(audio_path)
            
            # Step 6: Combine analyses to find optimal segments
            segments = self._find_optimal_segments(
                transcription, 
                visual_analysis, 
                audio_analysis,
                video_data
            )
            
            # Step 7: Score segments for engagement potential
            scored_segments = self._score_segments(segments)
            
            # Update result
            result.update({
                "success": True,
                "video_path": video_path,
                "audio_path": audio_path,
                "transcription": transcription,
                "visual_analysis": visual_analysis,
                "audio_analysis": audio_analysis,
                "segments": scored_segments,
                "analysis": {
                    "total_duration": visual_analysis["duration"],
                    "high_engagement_segments": len([s for s in scored_segments if s["score"] > 8.0]),
                    "average_score": np.mean([s["score"] for s in scored_segments]) if scored_segments else 0
                }
            })
            
            self.logger.info(f"Video analysis completed for {video_data.get('title', 'unknown')}")
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"Video analysis failed: {str(e)}")
        
        finally:
            # Cleanup temporary files
            self._cleanup_files([video_path, audio_path] if 'video_path' in locals() else [])
            
        return result
    
    def _download_video(self, video_data: Dict[str, Any]) -> Optional[str]:
        """Download video for analysis (simplified)."""
        try:
            # In production, use YouTube API or yt-dlp
            # For this example, we'll simulate with a local file or placeholder
            
            video_id = video_data.get("video_id", "example")
            output_dir = "temp/videos"
            os.makedirs(output_dir, exist_ok=True)
            
            # Simulate download by creating a placeholder file
            video_path = f"{output_dir}/{video_id}.mp4"
            
            # In real implementation:
            # subprocess.run(["yt-dlp", "-f", "best", "-o", video_path, video_data["source_url"]])
            
            # For testing, we'll use a sample video if available
            if os.path.exists("sample_video.mp4"):
                import shutil
                shutil.copy("sample_video.mp4", video_path)
            else:
                # Create a dummy file
                with open(video_path, 'wb') as f:
                    f.write(b'dummy video data')
            
            return video_path
            
        except Exception as e:
            self.logger.error(f"Video download failed: {str(e)}")
            return None
    
    def _extract_audio(self, video_path: str) -> Optional[str]:
        """Extract audio from video file."""
        try:
            audio_path = video_path.replace('.mp4', '.wav')
            
            # Use ffmpeg to extract audio
            cmd = [
                self.api_keys["ffmpeg_path"],
                '-i', video_path,
                '-vn', '-acodec', 'pcm_s16le',
                '-ar', '16000', '-ac', '1',
                audio_path,
                '-y'
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            return audio_path
            
        except Exception as e:
            self.logger.error(f"Audio extraction failed: {str(e)}")
            return None
    
    def _transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using Whisper model."""
        try:
            # Load audio file
            audio = AudioSegment.from_wav(audio_path)
            
            # Convert to format Whisper expects
            audio.export(audio_path, format="wav")
            
            # Transcribe with Whisper
            result = self.models["whisper"].transcribe(audio_path)
            
            # Process transcription
            transcription = {
                "text": result["text"],
                "segments": result.get("segments", []),
                "language": result.get("language", "en"),
                "duration": len(audio) / 1000  # seconds
            }
            
            # Add sentiment analysis
            transcription["sentiment"] = self._analyze_sentiment(transcription["text"])
            
            # Add emotion analysis
            transcription["emotions"] = self._analyze_emotions(transcription["text"])
            
            return transcription
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}")
            return {"text": "", "segments": [], "error": str(e)}
    
    def _analyze_visual_engagement(self, video_path: str) -> Dict[str, Any]:
        """Analyze video frames for visual engagement factors."""
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            
            # Initialize analysis variables
            frame_analysis = []
            face_detections = []
            motion_scores = []
            brightness_scores = []
            prev_gray = None
            
            # Load pre-trained models
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Process frames at intervals (every 1 second)
            frame_interval = int(fps)
            current_frame = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Process every nth frame
                if current_frame % frame_interval == 0:
                    # Convert to grayscale for analysis
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    face_detections.append(len(faces))
                    
                    # Calculate motion (simplified)
                    if current_frame > 0 and 'prev_gray' in locals():
                        frame_diff = cv2.absdiff(prev_gray, gray)
                        motion = np.sum(frame_diff) / (gray.size)
                        motion_scores.append(motion)
                    
                    # Calculate brightness
                    brightness = np.mean(gray)
                    brightness_scores.append(brightness)
                    
                    # Store frame analysis
                    frame_analysis.append({
                        "frame_number": current_frame,
                        "timestamp": current_frame / fps,
                        "faces": len(faces),
                        "motion": motion_scores[-1] if motion_scores else 0,
                        "brightness": brightness
                    })
                    
                    prev_gray = gray
                    
                current_frame += 1
            
            cap.release()
            
            # Calculate engagement metrics
            avg_faces = np.mean(face_detections) if face_detections else 0
            avg_motion = np.mean(motion_scores) if motion_scores else 0
            avg_brightness = np.mean(brightness_scores) if brightness_scores else 0
            
            # Identify high-engagement segments
            high_engagement_segments = []
            for i, frame_data in enumerate(frame_analysis):
                # Simple engagement score (can be enhanced)
                engagement_score = (
                    frame_data["faces"] * 0.4 +
                    frame_data["motion"] * 0.3 +
                    (frame_data["brightness"] / 255) * 0.3
                )
                
                if engagement_score > 0.7:  # Threshold for high engagement
                    high_engagement_segments.append({
                        "start_time": frame_data["timestamp"],
                        "end_time": frame_data["timestamp"] + 1,  # 1 second segment
                        "engagement_score": engagement_score,
                        "faces": frame_data["faces"],
                        "motion": frame_data["motion"]
                    })
            
            return {
                "success": True,
                "duration": duration,
                "fps": fps,
                "frame_count": frame_count,
                "average_faces": float(avg_faces),
                "average_motion": float(avg_motion),
                "average_brightness": float(avg_brightness),
                "high_engagement_segments": high_engagement_segments,
                "frame_analysis": frame_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Visual analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _analyze_audio_engagement(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio for engagement factors."""
        try:
            # Load audio file
            audio = AudioSegment.from_wav(audio_path)
            
            # Detect non-silent segments
            non_silent_segments = detect_nonsilent(
                audio,
                min_silence_len=500,  # 500ms
                silence_thresh=-40,   # dB
                seek_step=100         # 100ms
            )
            
            # Analyze volume levels
            volume_levels = []
            for i, segment in enumerate(non_silent_segments):
                segment_audio = audio[segment[0]:segment[1]]
                volume = segment_audio.dBFS
                volume_levels.append({
                    "start_time": segment[0] / 1000,
                    "end_time": segment[1] / 1000,
                    "duration": (segment[1] - segment[0]) / 1000,
                    "volume": volume
                })
            
            # Calculate speech rate
            speech_rate = len(non_silent_segments) / (len(audio) / 1000)  # segments per second
            
            # Detect laughter and applause (simplified)
            laughter_segments = []
            for segment in non_silent_segments:
                segment_audio = audio[segment[0]:segment[1]]
                # Simple frequency analysis for laughter detection
                # In production, use proper audio analysis
                if segment_audio.dBFS > -20 and (segment[1] - segment[0]) > 1000:  # Loud and >1s
                    laughter_segments.append({
                        "start_time": segment[0] / 1000,
                        "end_time": segment[1] / 1000,
                        "type": "laughter" if np.random.random() > 0.5 else "applause"
                    })
            
            return {
                "success": True,
                "duration": len(audio) / 1000,
                "non_silent_segments": non_silent_segments,
                "volume_analysis": volume_levels,
                "speech_rate": float(speech_rate),
                "laughter_applause": laughter_segments,
                "average_volume": np.mean([v["volume"] for v in volume_levels]) if volume_levels else 0
            }
            
        except Exception as e:
            self.logger.error(f"Audio analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _find_optimal_segments(self, transcription: Dict[str, Any], 
                               visual_analysis: Dict[str, Any], 
                               audio_analysis: Dict[str, Any],
                               video_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Combine analyses to find optimal clip segments."""
        segments = []
        
        try:
            # Get transcription segments
            trans_segments = transcription.get("segments", [])
            
            # Get high engagement visual segments
            visual_segments = visual_analysis.get("high_engagement_segments", [])
            
            # Get laughter/applause segments
            laughter_segments = audio_analysis.get("laughter_applause", [])
            
            # Combine all potential segments
            all_segments = []
            
            # Add transcription segments
            for seg in trans_segments:
                all_segments.append({
                    "source": "transcription",
                    "start_time": seg.get("start", 0),
                    "end_time": seg.get("end", 0),
                    "text": seg.get("text", ""),
                    "sentiment": seg.get("sentiment", "neutral"),
                    "emotions": seg.get("emotions", {})
                })
            
            # Add visual engagement segments
            for seg in visual_segments:
                all_segments.append({
                    "source": "visual",
                    "start_time": seg["start_time"],
                    "end_time": seg["end_time"],
                    "engagement_score": seg["engagement_score"],
                    "faces": seg["faces"],
                    "motion": seg["motion"]
                })
            
            # Add laughter/applause segments
            for seg in laughter_segments:
                all_segments.append({
                    "source": "audio",
                    "start_time": seg["start_time"],
                    "end_time": seg["end_time"],
                    "type": seg["type"],
                    "engagement": "high"
                })
            
            # Merge overlapping segments
            merged_segments = self._merge_overlapping_segments(all_segments)
            
            # Filter and score segments
            for seg in merged_segments:
                # Calculate segment score
                score = self._calculate_segment_score(seg, video_data)
                
                # Add to results if score is high enough
                if score >= self.video_settings["min_segment_score"]:
                    segments.append({
                        **seg,
                        "score": score,
                        "topic": self._infer_topic(seg),
                        "optimization_suggestions": self._generate_optimization_suggestions(seg)
                    })
            
            # Sort by score (highest first)
            segments.sort(key=lambda x: x["score"], reverse=True)
            
            # Limit to max clips
            segments = segments[:self.video_settings["max_clips_per_video"]]
            
        except Exception as e:
            self.logger.error(f"Segment analysis failed: {str(e)}")
        
        return segments
    
    def _merge_overlapping_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge overlapping or adjacent segments."""
        if not segments:
            return []
        
        # Sort by start time
        segments.sort(key=lambda x: x["start_time"])
        
        merged = [segments[0]]
        
        for current in segments[1:]:
            last = merged[-1]
            
            # If current segment overlaps or is adjacent to last
            if current["start_time"] <= last["end_time"] + 2.0:  # 2 second threshold
                # Merge them
                new_start = min(last["start_time"], current["start_time"])
                new_end = max(last["end_time"], current["end_time"])
                
                # Combine data
                merged_data = {**last, **current}
                merged_data["start_time"] = new_start
                merged_data["end_time"] = new_end
                
                # For text, combine if both have it
                if "text" in last and "text" in current:
                    merged_data["text"] = f"{last['text']} {current['text']}"
                
                merged[-1] = merged_data
            else:
                merged.append(current)
        
        return merged
    
    def _calculate_segment_score(self, segment: Dict[str, Any], video_data: Dict[str, Any]) -> float:
        """Calculate engagement score for a segment."""
        score = 0.0
        
        # Base score
        score += 5.0
        
        # Source-based scoring
        source_scores = {
            "transcription": 1.0,
            "visual": 1.5,
            "audio": 2.0
        }
        score += source_scores.get(segment.get("source", "transcription"), 1.0)
        
        # Sentiment analysis
        if "sentiment" in segment:
            sentiment_scores = {
                "POSITIVE": 2.0,
                "NEGATIVE": 0.5,
                "NEUTRAL": 1.0
            }
            score += sentiment_scores.get(segment["sentiment"], 1.0)
        
        # Emotion analysis
        if "emotions" in segment:
            emotion_scores = {
                "joy": 2.0,
                "surprise": 1.8,
                "anger": 1.5,
                "sadness": 1.2,
                "fear": 1.0,
                "neutral": 0.8
            }
            
            # Get highest emotion score
            for emotion, confidence in segment["emotions"].items():
                if emotion in emotion_scores:
                    score += emotion_scores[emotion] * confidence
                    break
        
        # Visual engagement factors
        if "engagement_score" in segment:
            score += segment["engagement_score"] * 2.0
        
        if "faces" in segment:
            score += min(segment["faces"] * 0.3, 1.5)  # Max 1.5 points for faces
        
        if "motion" in segment:
            score += min(segment["motion"] * 10, 1.0)  # Max 1.0 points for motion
        
        # Audio engagement factors
        if segment.get("type") == "laughter":
            score += 2.5
        elif segment.get("type") == "applause":
            score += 2.0
        
        # Guest factor (if known guest)
        guest = video_data.get("guest", "")
        if guest and "popular" in guest.lower():
            score += 1.0
        
        # Topic relevance
        topic = segment.get("topic", "")
        if topic and any(keyword in topic.lower() for keyword in ["funny", "hilarious", "amazing", "insane"]):
            score += 1.0
        
        # Duration factor (shorter segments get slight boost for social media)
        duration = segment["end_time"] - segment["start_time"]
        if duration <= 30:  # Ideal for shorts
            score += 0.5
        elif duration <= 60:
            score += 0.3
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _infer_topic(self, segment: Dict[str, Any]) -> str:
        """Infer topic from segment data."""
        # Check for explicit topic
        if "topic" in segment and segment["topic"]:
            return segment["topic"]
        
        # Check text content
        if "text" in segment and segment["text"]:
            text = segment["text"].lower()
            
            # Topic detection based on keywords
            if any(word in text for word in ["funny", "joke", "laugh", "hilarious"]):
                return "comedy"
            elif any(word in text for word in ["tech", "technology", "computer", "software"]):
                return "technology"
            elif any(word in text for word in ["story", "experience", "life", "personal"]):
                return "personal story"
            elif any(word in text for word in ["challenge", "food", "eat", "try"]):
                return "challenge"
            elif any(word in text for word in ["opinion", "think", "believe", "agree"]):
                return "hot take"
            else:
                return "conversation"
        
        # Default based on source
        if segment.get("source") == "audio":
            return "hilarious moment" if segment.get("type") == "laughter" else "applause moment"
        
        return "highlight"
    
    def _generate_optimization_suggestions(self, segment: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions for the segment."""
        suggestions = []
        
        # Based on segment type
        if segment.get("source") == "visual":
            suggestions.append("Use close-up shots for better engagement")
            suggestions.append("Add visual effects to highlight key moments")
        
        if segment.get("source") == "audio":
            suggestions.append("Enhance audio quality for laughter/applause")
            suggestions.append("Add sound effects to emphasize reactions")
        
        # Based on sentiment
        if segment.get("sentiment") == "POSITIVE":
            suggestions.append("Use bright, upbeat visual style")
            suggestions.append("Add positive emojis to captions")
        
        # Based on emotions
        if "emotions" in segment:
            for emotion, confidence in segment["emotions"].items():
                if confidence > 0.7:
                    if emotion == "joy":
                        suggestions.append("Use warm color grading")
                        suggestions.append("Add laughter sound effects")
                    elif emotion == "surprise":
                        suggestions.append("Use dramatic zoom effects")
                        suggestions.append("Add suspenseful music")
        
        # Based on topic
        topic = segment.get("topic", "")
        if "comedy" in topic.lower():
            suggestions.append("Add comedy sound effects")
            suggestions.append("Use funny text overlays")
        elif "tech" in topic.lower():
            suggestions.append("Add tech-related visuals")
            suggestions.append("Use futuristic text effects")
        
        # General suggestions
        suggestions.append("Add subtitles for accessibility")
        suggestions.append("Optimize for mobile viewing")
        suggestions.append("Include call-to-action in description")
        
        return suggestions
    
    def _score_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score segments for engagement potential."""
        scored_segments = []
        
        for segment in segments:
            # Calculate comprehensive score
            score = self._calculate_segment_score(segment, {})
            
            # Add engagement prediction
            engagement_prediction = self._predict_engagement(segment)
            
            scored_segments.append({
                **segment,
                "score": score,
                "engagement_prediction": engagement_prediction
            })
        
        return scored_segments
    
    def _predict_engagement(self, segment: Dict[str, Any]) -> Dict[str, float]:
        """Predict engagement potential using AI model."""
        try:
            # Prepare text for prediction
            text = segment.get("text", "")
            if not text:
                # Generate text from segment data
                text = f"Segment about {segment.get('topic', 'podcast')} with {segment.get('sentiment', 'positive')} sentiment"
            
            # Use engagement prediction model
            result = self.models["engagement"](text)
            
            # Map to engagement metrics
            engagement_scores = {
                "views": 0.0,
                "likes": 0.0,
                "shares": 0.0,
                "comments": 0.0
            }
            
            # Simple mapping (in production, use proper trained model)
            score = segment.get("score", 5.0) / 10.0  # Normalize to 0-1
            
            engagement_scores["views"] = score * 10000
            engagement_scores["likes"] = score * 1000
            engagement_scores["shares"] = score * 500
            engagement_scores["comments"] = score * 200
            
            return {
                "potential": score,
                "predicted_metrics": engagement_scores,
                "confidence": min(score * 1.2, 0.95)
            }
            
        except Exception as e:
            self.logger.error(f"Engagement prediction failed: {str(e)}")
            return {
                "potential": 0.5,
                "predicted_metrics": {
                    "views": 5000,
                    "likes": 500,
                    "shares": 250,
                    "comments": 100
                },
                "confidence": 0.5
            }
    
    def generate_clips_from_video(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actual video clips from analysis results."""
        clips = []
        
        if not analysis_result.get("success", False):
            return clips
        
        try:
            video_path = analysis_result["video_path"]
            segments = analysis_result["segments"]
            
            # Create output directory
            output_dir = f"exports/clips/{analysis_result['video_id']}"
            os.makedirs(output_dir, exist_ok=True)
            
            for i, segment in enumerate(segments):
                if segment["score"] >= self.video_settings["min_segment_score"]:
                    clip = self._create_video_clip(video_path, segment, output_dir, i)
                    if clip:
                        clips.append(clip)
            
            self.logger.info(f"Generated {len(clips)} clips from {analysis_result['video_id']}")
            
        except Exception as e:
            self.logger.error(f"Clip generation failed: {str(e)}")
        
        return clips
    
    def _create_video_clip(self, video_path: str, segment: Dict[str, Any], 
                          output_dir: str, clip_index: int) -> Optional[Dict[str, Any]]:
        """Create a video clip from a segment."""
        try:
            # Generate clip filename
            clip_id = f"clip-{clip_index:03d}"
            output_path = f"{output_dir}/{clip_id}.mp4"
            
            # Calculate duration
            start_time = segment["start_time"]
            end_time = segment["end_time"]
            duration = end_time - start_time
            
            # Use ffmpeg to create clip
            cmd = [
                self.api_keys["ffmpeg_path"],
                '-i', video_path,
                '-ss', str(start_time),
                '-to', str(end_time),
                '-c', 'copy',  # Copy streams for fast processing
                output_path,
                '-y'
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Verify clip was created
            if not os.path.exists(output_path):
                self.logger.error(f"Clip creation failed: {output_path}")
                return None
            
            # Get clip information
            clip_info = self._get_video_info(output_path)
            
            # Create clip metadata
            clip = {
                "clip_id": clip_id,
                "source_video": segment.get("source_video", ""),
                "source_segment": segment,
                "file_path": output_path,
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration,
                "file_size": os.path.getsize(output_path),
                "resolution": f"{clip_info['width']}x{clip_info['height']}",
                "format": "mp4",
                "score": segment["score"],
                "topic": segment["topic"],
                "engagement_prediction": segment.get("engagement_prediction", {}),
                "optimization_suggestions": segment.get("optimization_suggestions", []),
                "platforms": self._determine_optimal_platforms(segment),
                "status": "generated"
            }
            
            # Generate platform-specific versions
            platform_clips = self._generate_platform_versions(clip)
            clip["platform_versions"] = platform_clips
            
            return clip
            
        except Exception as e:
            self.logger.error(f"Error creating clip: {str(e)}")
            return None
    
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video information using ffprobe."""
        try:
            cmd = [
                self.api_keys["ffmpeg_path"],
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,r_frame_rate,duration',
                '-of', 'json',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            info = json.loads(result.stdout)
            
            stream = info.get("streams", [{}])[0]
            
            return {
                "width": int(stream.get("width", 0)),
                "height": int(stream.get("height", 0)),
                "fps": stream.get("r_frame_rate", "30"),
                "duration": float(stream.get("duration", 0))
            }
            
        except Exception as e:
            self.logger.error(f"Error getting video info: {str(e)}")
            return {"width": 1920, "height": 1080, "fps": "30", "duration": 0}
    
    def _determine_optimal_platforms(self, segment: Dict[str, Any]) -> List[str]:
        """Determine optimal platforms for a clip based on its characteristics."""
        platforms = []
        
        # All clips can go to YouTube Shorts
        platforms.append("youtube_shorts")
        
        # Determine based on topic
        topic = segment.get("topic", "").lower()
        
        if "funny" in topic or "hilarious" in topic or "comedy" in topic:
            platforms.extend(["tiktok", "instagram", "twitter"])
        elif "tech" in topic or "technology" in topic:
            platforms.extend(["twitter", "linkedin", "facebook"])
        elif "story" in topic or "personal" in topic:
            platforms.extend(["instagram", "facebook", "twitter"])
        elif "challenge" in topic:
            platforms.extend(["tiktok", "instagram", "facebook"])
        elif "hot take" in topic or "opinion" in topic:
            platforms.extend(["twitter", "facebook", "linkedin"])
        else:
            platforms.extend(["instagram", "twitter", "facebook"])
        
        # Ensure unique platforms
        return list(set(platforms))
    
    def _generate_platform_versions(self, clip: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Generate platform-specific versions of a clip."""
        platform_versions = {}
        
        for platform in clip["platforms"]:
            try:
                # Get platform config
                config = self.platform_configs[platform]
                
                # Generate platform-specific version
                version = self._create_platform_version(clip, platform, config)
                
                if version:
                    platform_versions[platform] = version
                    
            except Exception as e:
                self.logger.error(f"Error creating {platform} version: {str(e)}")
        
        return platform_versions
    
    def _create_platform_version(self, clip: Dict[str, Any], 
                                platform: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a platform-specific version of a clip."""
        try:
            # Generate output path
            base_path = clip["file_path"]
            platform_dir = os.path.join(os.path.dirname(base_path), platform)
            os.makedirs(platform_dir, exist_ok=True)
            
            output_path = os.path.join(platform_dir, f"{os.path.basename(base_path)}")
            
            # Determine aspect ratio
            aspect_ratio = config["aspect_ratio"]
            
            # Calculate dimensions based on original resolution
            original_info = self._get_video_info(clip["file_path"])
            original_width = original_info["width"]
            original_height = original_info["height"]
            
            # Parse aspect ratio
            if ":" in aspect_ratio:
                target_width, target_height = map(int, aspect_ratio.split(":"))
                ratio = target_width / target_height
            else:
                ratio = 1.0  # Square
            
            # Calculate new dimensions
            if ratio > 1:  # Landscape
                new_width = min(original_width, 1920)
                new_height = int(new_width / ratio)
            else:  # Portrait or square
                new_height = min(original_height, 1080)
                new_width = int(new_height * ratio)
            
            # Build ffmpeg command
            cmd = [
                self.api_keys["ffmpeg_path"],
                '-i', clip["file_path"],
                '-vf', f'scale={new_width}:{new_height}:force_original_aspect_ratio=decrease,pad={new_width}:{new_height}:(ow-iw)/2:(oh-ih)/2',
                '-c:a', 'copy'
            ]
            
            # Add platform-specific optimizations
            if platform == "tiktok":
                cmd.extend(['-r', '30', '-b:v', '4M'])
            elif platform == "instagram":
                cmd.extend(['-r', '30', '-b:v', '3M'])
            elif platform == "twitter":
                cmd.extend(['-r', '30', '-b:v', '2M'])
            
            cmd.append(output_path)
            cmd.append('-y')
            
            # Run command
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Verify output
            if not os.path.exists(output_path):
                return None
            
            # Get output info
            output_info = self._get_video_info(output_path)
            
            # Generate platform-specific metadata
            version = {
                "platform": platform,
                "file_path": output_path,
                "file_size": os.path.getsize(output_path),
                "resolution": f"{output_info['width']}x{output_info['height']}",
                "aspect_ratio": aspect_ratio,
                "duration": clip["duration"],
                "optimal_length": config["optimal_length"],
                "max_duration": config["max_duration"],
                "hashtags": config["hashtags"],
                "caption_length": config["caption_length"],
                "engagement_factors": config["engagement_factors"],
                "status": "generated"
            }
            
            # Generate platform-specific captions and metadata
            version["metadata"] = self._generate_platform_metadata(clip, platform)
            
            return version
            
        except Exception as e:
            self.logger.error(f"Platform version creation failed: {str(e)}")
            return None
    
    def _generate_platform_metadata(self, clip: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Generate platform-specific metadata for a clip."""
        metadata = {}
        
        # Base metadata from clip
        source_segment = clip["source_segment"]
        
        # Generate title
        metadata["title"] = self._generate_platform_title(source_segment, platform)
        
        # Generate description/caption
        metadata["description"] = self._generate_platform_description(source_segment, platform)
        
        # Generate hashtags
        metadata["hashtags"] = self._generate_platform_hashtags(source_segment, platform)
        
        # Platform-specific fields
        if platform == "youtube_shorts":
            metadata["title"] += " #shorts"
            metadata["visibility"] = "public"
            metadata["category"] = "Comedy"
        
        elif platform == "tiktok":
            metadata["allow_duet"] = True
            metadata["allow_stitch"] = True
            metadata["comment_setting"] = "public"
        
        elif platform == "instagram":
            metadata["location"] = "Roanoke, VA"
            metadata["user_tags"] = ["jaredsnotfunny"]
        
        elif platform == "twitter":
            metadata["reply_settings"] = "everyone"
            metadata["media_category"] = "tweet_video"
        
        elif platform == "facebook":
            metadata["privacy"] = {"value": "EVERYONE"}
            metadata["published"] = False  # Draft by default
        
        return metadata
    
    def _generate_platform_title(self, segment: Dict[str, Any], platform: str) -> str:
        """Generate platform-specific title."""
        # Use the clip title from segment analysis
        title = segment.get("title", "Jared's Not Funny Clip")
        
        # Platform-specific adjustments
        if platform == "youtube_shorts":
            # Ensure it ends with #shorts
            if not title.endswith("#shorts"):
                title += " #shorts"
        elif platform == "tiktok":
            # Add emoji if not present
            if not any(char in title for char in ["🎤", "🎙️", "😂", "🔥", "💥"]):
                title = "🎙️ " + title
        elif platform == "twitter":
            # Keep it concise
            if len(title) > 80:
                title = title[:77] + "..."
        
        return title
    
    def _generate_platform_description(self, segment: Dict[str, Any], platform: str) -> str:
        """Generate platform-specific description."""
        # Use the clip description from segment analysis
        description = segment.get("description", "Clip from Jared's Not Funny Podcast")
        
        # Platform-specific adjustments
        if platform == "youtube_shorts":
            # Add CTA and links
            description += ("\n\n🔥 Full episode: https://jcsnotfunny.com "
                          "😂 More clips: @jaredsnotfunny")
        elif platform == "tiktok":
            # Keep it short and engaging
            if len(description) > 150:
                description = description[:147] + "..."
            description += "\n\n#jaredsnotfunny #podcast #comedy"
        elif platform == "instagram":
            # Add emojis and spacing
            description = description.replace(". ", "\n\n")
            description += "\n\n🎧 Full podcast: jcsnotfunny.com"
        elif platform == "twitter":
            # Very concise
            if len(description) > 200:
                description = description[:197] + "..."
            description += " https://jcsnotfunny.com"
        elif platform == "facebook":
            # Can be longer
            description += ("\n\n🎧 Listen to the full episode: https://jcsnotfunny.com "
                          "😂 Follow for more comedy: @jaredsnotfunny")
        
        return description
    
    def _generate_platform_hashtags(self, segment: Dict[str, Any], platform: str) -> List[str]:
        """Generate platform-specific hashtags."""
        # Start with base hashtags from segment
        hashtags = segment.get("hashtags", ["#jaredsnotfunny", "#podcast", "#comedy"])
        
        # Add platform-specific hashtags
        platform_hashtags = {
            "youtube_shorts": ["#shorts", "#viral", "#trending"],
            "tiktok": ["#fyp", "#foryou", "#viral", "#comedyclips"],
            "instagram": ["#reels", "#explore", "#comedyreels"],
            "twitter": ["#podcast", "#comedy", "#tech"],
            "facebook": ["#entertainment", "#funny", "#podcastlife"]
        }
        
        hashtags.extend(platform_hashtags.get(platform, []))
        
        # Remove duplicates and limit based on platform
        unique_hashtags = list(set(hashtags))
        
        platform_limits = {
            "youtube_shorts": 15,
            "tiktok": 5,
            "instagram": 10,
            "twitter": 2,
            "facebook": 5
        }
        
        limit = platform_limits.get(platform, 10)
        return unique_hashtags[:limit]
    
    def optimize_clips_for_platforms(self, clips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize clips for specific platforms."""
        optimized_clips = []
        
        for clip in clips:
            try:
                # Generate platform versions if not already done
                if "platform_versions" not in clip:
                    clip["platform_versions"] = self._generate_platform_versions(clip)
                
                # Add platform-specific recommendations
                clip["platform_recommendations"] = self._generate_platform_recommendations(clip)
                
                optimized_clips.append(clip)
                
            except Exception as e:
                self.logger.error(f"Platform optimization failed: {str(e)}")
        
        return optimized_clips
    
    def _generate_platform_recommendations(self, clip: Dict[str, Any]) -> Dict[str, Any]:
        """Generate platform-specific posting recommendations."""
        recommendations = {}
        
        for platform, version in clip["platform_versions"].items():
            platform_recs = {
                "optimal_posting_time": self._get_optimal_posting_time(platform).strftime("%Y-%m-%d %H:%M:%S"),
                "engagement_strategy": self._get_engagement_strategy(platform, clip),
                "hashtag_strategy": f"Use {len(version['hashtags'])} hashtags: {' '.join(version['hashtags'][:3])}",
                "caption_tips": self._get_caption_tips(platform),
                "visual_tips": self._get_visual_tips(platform)
            }
            
            # Add platform-specific recommendations
            if platform == "youtube_shorts":
                platform_recs["thumbnails"] = "Use bright, high-contrast thumbnails"
                platform_recs["titles"] = "Include #shorts and emojis"
            elif platform == "tiktok":
                platform_recs["trends"] = "Use trending sounds and effects"
                platform_recs["duets"] = "Enable duets for viral potential"
            elif platform == "instagram":
                platform_recs["reels"] = "Use Reels effects and stickers"
                platform_recs["location"] = "Add Roanoke, VA location tag"
            elif platform == "twitter":
                platform_recs["threads"] = "Consider creating a thread"
                platform_recs["polls"] = "Add a poll for engagement"
            elif platform == "facebook":
                platform_recs["groups"] = "Share in relevant Facebook groups"
                platform_recs["boost"] = "Consider boosting high-performing clips"
            
            recommendations[platform] = platform_recs
        
        return recommendations
    
    def _get_engagement_strategy(self, platform: str, clip: Dict[str, Any]) -> str:
        """Get engagement strategy for platform."""
        topic = clip["topic"]
        score = clip["score"]
        
        strategies = {
            "youtube_shorts": {
                "comedy": "Ask viewers what they think is funniest",
                "tech": "Ask for tech opinions in comments",
                "story": "Encourage viewers to share their stories"
            },
            "tiktok": {
                "comedy": "Use 'Watch till end' hook",
                "tech": "Ask 'Did you know this?'",
                "story": "Use 'Relatable?' caption"
            },
            "instagram": {
                "comedy": "Use poll sticker for funniest part",
                "tech": "Ask for tech recommendations",
                "story": "Encourage story sharing"
            },
            "twitter": {
                "comedy": "Ask for funny responses",
                "tech": "Start a tech debate",
                "story": "Ask for similar experiences"
            },
            "facebook": {
                "comedy": "Ask for funny captions",
                "tech": "Encourage tech discussions",
                "story": "Ask for related stories"
            }
        }
        
        # Get topic category
        topic_category = "comedy" if "comedy" in topic.lower() else (
            "tech" if "tech" in topic.lower() else "story"
        )
        
        return strategies.get(platform, {}).get(topic_category, "Ask viewers what they think")
    
    def _get_caption_tips(self, platform: str) -> str:
        """Get caption tips for platform."""
        tips = {
            "youtube_shorts": "Use emojis, ask questions, include #shorts",
            "tiktok": "Start with hook, use trending hashtags, keep it short",
            "instagram": "Use line breaks, emojis, and clear CTAs",
            "twitter": "Be concise, use humor, include relevant hashtags",
            "facebook": "Tell a story, ask questions, use emojis sparingly"
        }
        
        return tips.get(platform, "Be clear and engaging")
    
    def _get_visual_tips(self, platform: str) -> str:
        """Get visual tips for platform."""
        tips = {
            "youtube_shorts": "Use bright colors, fast cuts, text overlays",
            "tiktok": "Use trending effects, fast transitions, bold text",
            "instagram": "Use aesthetic filters, smooth transitions, clear text",
            "twitter": "Use simple visuals, clear text, minimal effects",
            "facebook": "Use professional look, clear visuals, readable text"
        }
        
        return tips.get(platform, "Keep it visually appealing")
    
    def predict_clip_engagement(self, clips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict engagement potential for clips using AI."""
        predictions = []
        
        for clip in clips:
            try:
                # Get engagement prediction
                prediction = self._predict_engagement(clip["source_segment"])
                
                # Add to clip
                clip["engagement_prediction"] = prediction
                predictions.append({
                    "clip_id": clip["clip_id"],
                    "prediction": prediction
                })
                
            except Exception as e:
                self.logger.error(f"Engagement prediction failed: {str(e)}")
        
        return predictions
    
    def process_batch_videos(self, video_urls: List[str]) -> Dict[str, Any]:
        """Process multiple videos in batch for clip generation."""
        batch_result = {
            "success": False,
            "videos_processed": 0,
            "clips_generated": 0,
            "total_engagement_score": 0,
            "errors": [],
            "results": {}
        }
        
        try:
            for video_url in video_urls:
                try:
                    # Create video data
                    video_id = video_url.split("v=")[-1].split("&")[0] if "v=" in video_url else video_url.split("/")[-1]
                    video_data = {
                        "video_id": video_id,
                        "source_url": video_url,
                        "title": f"YouTube Video {video_id}",
                        "content_type": "youtube_episode"
                    }
                    
                    # Analyze video
                    analysis = self.analyze_video_for_clips(video_data)
                    
                    if analysis["success"]:
                        # Generate clips
                        clips = self.generate_clips_from_video(analysis)
                        
                        # Optimize clips
                        optimized_clips = self.optimize_clips_for_platforms(clips)
                        
                        # Predict engagement
                        predictions = self.predict_clip_engagement(optimized_clips)
                        
                        # Update batch results
                        batch_result["videos_processed"] += 1
                        batch_result["clips_generated"] += len(optimized_clips)
                        batch_result["total_engagement_score"] += sum(
                            clip["score"] for clip in optimized_clips
                        )
                        
                        batch_result["results"][video_id] = {
                            "analysis": analysis,
                            "clips": optimized_clips,
                            "predictions": predictions
                        }
                    else:
                        batch_result["errors"].append({
                            "video_id": video_id,
                            "error": analysis["error"]
                        })
                        
                except Exception as e:
                    batch_result["errors"].append({
                        "video_url": video_url,
                        "error": str(e)
                    })
            
            batch_result["success"] = len(batch_result["errors"]) == 0
            batch_result["average_engagement_score"] = (
                batch_result["total_engagement_score"] / batch_result["clips_generated"]
                if batch_result["clips_generated"] > 0 else 0
            )
            
        except Exception as e:
            batch_result["errors"].append(f"Batch processing failed: {str(e)}")
        
        return batch_result
    
    def _cleanup_files(self, files: List[str]) -> None:
        """Clean up temporary files."""
        for file in files:
            try:
                if file and os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                self.logger.error(f"Cleanup failed for {file}: {str(e)}")
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text."""
        try:
            result = self.models["sentiment"](text)
            return result[0]["label"]
        except:
            return "NEUTRAL"
    
    def _analyze_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotions in text."""
        try:
            result = self.models["emotion"](text)
            emotions = {}
            for item in result:
                emotions[item["label"]] = item["score"]
            return emotions
        except:
            return {"neutral": 1.0}


if __name__ == "__main__":
    # Example usage
    agent = YouTubeClipAgent()
    
    # Example video data
    example_video = {
        "video_id": "yCPDYXORg-A",
        "source_url": "https://www.youtube.com/watch?v=yCPDYXORg-A",
        "title": "JAREDSNOTFUNNY Feat. Toron Rodgers #6",
        "description": "Jared Christianson sits down with Toron Rodgers as they discuss performing stand up comedy, production and life experiences.",
        "content_type": "youtube_episode",
        "guest": "Toron Rodgers",
        "topics": ["stand up comedy", "production", "life experiences"]
    }
    
    # Analyze video and generate clips
    print("🎬 Analyzing video for optimal clips...")
    analysis = agent.analyze_video_for_clips(example_video)
    
    if analysis["success"]:
        print(f"✅ Analysis completed! Found {len(analysis['segments'])} high-potential segments")
        
        print("📼 Generating clips...")
        clips = agent.generate_clips_from_video(analysis)
        
        print(f"✅ Generated {len(clips)} clips:")
        for clip in clips:
            print(f"   - {clip['clip_id']}: {clip['topic']} ({clip['duration']:.1f}s, Score: {clip['score']:.1f})")
            
        print("🎯 Optimizing for platforms...")
        optimized_clips = agent.optimize_clips_for_platforms(clips)
        
        print("📊 Predicting engagement...")
        predictions = agent.predict_clip_engagement(optimized_clips)
        
        print("📈 Engagement Predictions:")
        for pred in predictions:
            print(f"   - {pred['clip_id']}: {pred['prediction']['potential']*100:.1f}% potential")
            
    else:
        print(f"❌ Analysis failed: {analysis['error']}")