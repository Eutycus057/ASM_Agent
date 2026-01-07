import os
from moviepy import ImageClip, AudioFileClip, VideoFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips
import moviepy.video.fx as vfx
import moviepy.audio.fx as afx
from typing import List, Optional

class CharacterAnimator:
    def __init__(self, output_dir: str = "frontend/assets"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def assemble_multi_scene_video(self, video_paths: List[str], voice_path: str, output_filename: str, music_path: Optional[str] = None) -> Optional[str]:
        """
        Concatenates multiple cinematic clips with smooth crossfades and adds dual-track audio.
        Uses a robust padding/fading approach to eliminate black frames.
        """
        try:
            print(f"--- Assembling Multi-Scene Cinematic Video (with Fades): {output_filename} ---")
            voice_audio = AudioFileClip(voice_path)
            
            raw_clips = []
            for path in video_paths:
                if os.path.exists(path):
                    clip = VideoFileClip(path)
                    # Standardize height and ensure 24fps for stability
                    if clip.h != 1080:
                        clip = clip.resized(height=1080)
                    clip = clip.with_fps(24)
                    raw_clips.append(clip)
            
            if not raw_clips:
                print("No valid video clips found for assembly.")
                return None
            
            # Implementation of smooth crossfades
            fade_duration = 0.5

            final_video = concatenate_videoclips(
                raw_clips,
                method="compose",
                padding=-fade_duration
            )

            # Match video length to voice length
            if final_video.duration < voice_audio.duration:
                # Calculate necessary loops
                num_loops = int(voice_audio.duration / final_video.duration) + 1
                final_video = final_video.with_effects([vfx.Loop(n=num_loops)])
            
            # Trim to voice duration
            final_video = final_video.with_duration(voice_audio.duration)
            
            # Handle background music
            final_audio = voice_audio
            if music_path and os.path.exists(music_path):
                try:
                    print(f"Layering background music: {music_path}")
                    bg_music = AudioFileClip(music_path)
                    
                    if bg_music.duration > 0:
                        # Loop music to match video
                        if bg_music.duration < final_video.duration:
                            from moviepy.audio.fx import audio_loop
                            bg_music = audio_loop(bg_music, duration=final_video.duration)
                        
                        # Trim and lower volume
                        bg_music = bg_music.with_duration(final_video.duration).fx(afx.MultiplyVolume, 0.15)
                        
                        # Mix voice and bg music
                        from moviepy.audio.AudioClip import CompositeAudioClip
                        final_audio = CompositeAudioClip([voice_audio, bg_music])
                    else:
                        print("Background music has 0 duration, skipping.")
                except Exception as e:
                    print(f"Warning: Could not layer background music ({e}). Falling back to voice only.")
                    final_audio = voice_audio

            # Final assembly
            final_clip = final_video.with_audio(final_audio)

            # 🔧 CRITICAL FIX: ensure even dimensions for H.264
            w, h = final_clip.size
            final_clip = final_clip.resized((w - w % 2, h - h % 2))

            output_path = os.path.join(self.output_dir, output_filename)

            final_clip.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=4,
                ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"]
            )

            # Close clips to free resources
            voice_audio.close()
            for c in raw_clips: c.close()
            final_clip.close()
            
            return output_path
        except Exception as e:
            print(f"Multi-Scene Assembly Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_cinematic_video(self, video_path: str, audio_path: str, output_filename: str) -> Optional[str]:
        # ... (existing method kept for single-scene fallback compatibility if needed)
        """
        Creates a cinematic video by combining an AI-generated clip with audio.
        Loops the video to match audio duration.
        """
        try:
            print(f"--- Assembling Cinematic Video: {output_filename} ---")
            audio = AudioFileClip(audio_path)
            
            if video_path and os.path.exists(video_path):
                print(f"Using generated cinematic video: {video_path}")
                base_video = VideoFileClip(video_path)
                
                # Loop the video to match audio duration
                num_loops = int(audio.duration / base_video.duration) + 1
                clip = base_video.with_effects([vfx.Loop(n=num_loops)]).with_duration(audio.duration)
                
                # Ensure correct aspect ratio/size (1080p height)
                if clip.h > 1080:
                    clip = clip.resized(height=1080)
            else:
                print("Generated video not found, falling back to color background...")
                # Fallback to a sleek dark background if video fails
                clip = ColorClip(size=(1920, 1080), color=(20, 20, 20)).with_duration(audio.duration)
            
            # Set audio directly
            final_clip = clip.with_audio(audio)
            
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Fast settings, forcing browser-safe pixel format
            final_clip.write_videofile(
                output_path, 
                fps=24, # Professional cinematic fps
                codec="libx264", 
                audio_codec="aac",
                preset="medium", # Better quality than ultrafast
                threads=4,
                ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"]
            )
            
            return output_path
        except Exception as e:
            print(f"Animation Error: {e}")
            return None

animator = CharacterAnimator()
