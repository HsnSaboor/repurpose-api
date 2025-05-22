import argparse
import logging
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import JSONFormatter, TextFormatter
import yt_dlp

logging.basicConfig(level=logging.INFO)

def fetch_transcript(video_id: str, lang_code: str = 'en') -> str:
    """Fetch YouTube transcript with fallback and translation logic."""
    logging.info(f"Attempting to fetch transcript for {video_id} in {lang_code}")
    
    # Try different methods in sequence
    transcript = None
    
    # 1. Try youtube_transcript_api first
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try requested language
        if lang_code in transcript_list._manually_created_transcripts:
            transcript = transcript_list.find_manually_created_transcript([lang_code]).fetch()
            logging.info(f"Found manual {lang_code} transcript")
            return TextFormatter().format_transcript(transcript)
            
        if lang_code in transcript_list._generated_transcripts:
            transcript = transcript_list.find_generated_transcript([lang_code]).fetch()
            logging.info(f"Found auto-generated {lang_code} transcript")
            return TextFormatter().format_transcript(transcript)
            
    except (TranscriptsDisabled, NoTranscriptFound, Exception) as e:
        logging.warning(f"Primary transcript fetch failed: {str(e)}")
        
        # 1. Try requested language (manual first, then auto)
        if lang_code in transcript_list._manually_created_transcripts:
            transcript = transcript_list.find_manually_created_transcript([lang_code])
            logging.info(f"Found manual {lang_code} transcript")
            return TextFormatter().format_transcript(transcript.fetch())
            
        if lang_code in transcript_list._generated_transcripts:
            transcript = transcript_list.find_generated_transcript([lang_code])
            logging.info(f"Found auto-generated {lang_code} transcript")
            return TextFormatter().format_transcript(transcript.fetch())

        # 2. Fallback to English (manual first, then auto)
        if lang_code != 'en':
            if 'en' in transcript_list._manually_created_transcripts:
                transcript = transcript_list.find_manually_created_transcript(['en'])
                logging.info("Found manual English transcript")
                return TextFormatter().format_transcript(transcript.fetch())
                
            if 'en' in transcript_list._generated_transcripts:
                transcript = transcript_list.find_generated_transcript(['en'])
                logging.info("Found auto-generated English transcript")
                return TextFormatter().format_transcript(transcript.fetch())

        # 3. Fallback to any available transcript (manual first, then auto)
        if transcript_list._manually_created_transcripts:
            transcript = next(iter(transcript_list._manually_created_transcripts.values()))
            logging.info(f"Found manual transcript in {transcript.language_code}")
            if transcript.language_code != lang_code:
                translated = attempt_translation(transcript, lang_code)
                if translated:
                    return translated
                else:
                    logging.info(f"Returning manual transcript in {transcript.language_code}")
                    return TextFormatter().format_transcript(transcript.fetch())
            else:
                return TextFormatter().format_transcript(transcript.fetch())
            
        if transcript_list._generated_transcripts:
            transcript = next(iter(transcript_list._generated_transcripts.values()))
            logging.info(f"Found auto-generated transcript in {transcript.language_code}")
            if transcript.language_code != lang_code:
                translated = attempt_translation(transcript, lang_code)
                if translated:
                    return translated
                else:
                    logging.info(f"Returning auto-generated transcript in {transcript.language_code}")
                    return TextFormatter().format_transcript(transcript.fetch())
            else:
                return TextFormatter().format_transcript(transcript.fetch())

        # 4. Final fallback to yt-dlp
        return fetch_transcript_yt_dlp(video_id, lang_code)

    # 2. Try yt-dlp as fallback
    try:
        transcript = fetch_transcript_yt_dlp(video_id, lang_code)
        if transcript:
            logging.info("Successfully fetched transcript using yt-dlp")
            return transcript
    except Exception as e:
        logging.warning(f"yt-dlp fallback failed: {str(e)}")
        
    # 3. Try auto-translation if available
    try:
        if transcript_list:
            # Try English first
            if 'en' in transcript_list._manually_created_transcripts:
                en_transcript = transcript_list.find_manually_created_transcript(['en'])
                translated = attempt_translation(en_transcript, lang_code)
                if translated:
                    return translated
                    
            # Try any available language
            for transcript in transcript_list._manually_created_transcripts.values():
                translated = attempt_translation(transcript, lang_code)
                if translated:
                    return translated
                    
    except Exception as e:
        logging.warning(f"Translation attempts failed: {str(e)}")
    
    logging.error(f"Failed to fetch transcript for {video_id} using all available methods")
    return None

def attempt_translation(transcript, target_lang):
    """Attempts to translate the transcript to the target language. Returns formatted transcript if successful, else None."""
    try:
        if not transcript.is_translatable:
            logging.warning(f"Transcript in {transcript.language_code} is not translatable.")
            return None

        available_langs = [tl['language_code'] for tl in transcript.translation_languages]
        if target_lang not in available_langs:
            logging.warning(f"Translation to {target_lang} not available. Available languages: {available_langs}")
            return None

        translated_transcript = transcript.translate(target_lang)
        logging.info(f"Translated transcript from {transcript.language_code} to {target_lang}")
        return TextFormatter().format_transcript(translated_transcript.fetch())
    except Exception as e:
        logging.error(f"Translation failed: {str(e)}")
        return None

def fetch_transcript_yt_dlp(video_id: str, lang_code: str) -> str:
    """
    Fallback transcript fetch using yt-dlp.
    
    Args:
        video_id: YouTube video ID
        lang_code: Language code for transcript
        
    Returns:
        str: Transcript text or None if not available
    """
    logging.info(f"Attempting to fetch transcript via yt-dlp for video {video_id} in {lang_code}")
    
    try:
        ydl_opts = {
            'writesubtitles': True,
            'subtitleslangs': [lang_code, 'en'],
            'skip_download': True,
            'quiet': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://youtu.be/{video_id}", download=False)
            
            if not info:
                logging.error(f"No video info retrieved for {video_id}")
                return None
                
            if not info.get('subtitles'):
                logging.warning(f"No subtitles found in video info for {video_id}")
                return None
            
            # Try requested language first, then English
            for lang in [lang_code, 'en']:
                if lang not in info['subtitles']:
                    logging.debug(f"Language {lang} not found in available subtitles for {video_id}")
                    continue
                    
                try:
                    subs_list = info['subtitles'][lang]
                    if not subs_list:
                        logging.warning(f"Empty subtitles list for {video_id} in {lang}")
                        continue
                        
                    subs = subs_list[0].get('data')
                    if not subs:
                        logging.warning(f"No subtitle data found for {video_id} in {lang}")
                        continue
                    
                    if isinstance(subs, list):
                        # Handle list format
                        transcript_data = []
                        for item in subs:
                            if not isinstance(item, dict):
                                continue
                            
                            text = item.get('text', '').strip()
                            if not text:
                                continue
                                
                            transcript_data.append({
                                'text': text,
                                'start': float(item.get('start', 0)),
                                'duration': float(item.get('duration', 0))
                            })
                            
                        if transcript_data:
                            logging.info(f"Successfully processed {len(transcript_data)} subtitle entries for {video_id}")
                            return TextFormatter().format_transcript(transcript_data)
                            
                    elif isinstance(subs, str):
                        # Handle plain text format
                        text = subs.strip()
                        if text:
                            logging.info(f"Retrieved plain text transcript for {video_id}")
                            return text
                            
                except Exception as sub_error:
                    logging.error(f"Error processing subtitles for {video_id} in {lang}: {str(sub_error)}")
                    continue
            
            logging.error(f"No valid subtitles found for {video_id} in any attempted language")
            return None

    except Exception as e:
        logging.error(f"yt-dlp fallback failed for {video_id}: {str(e)}")
        return None
