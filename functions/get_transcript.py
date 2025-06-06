import asyncio
from functions.send_message import send_message
from functions.whisper_transcript import whisper_transcript
from functions.get_video_id import get_video_id
import logging
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)


async def get_transcript(data):
    yt_vide_id = get_video_id(data.get("url"))
    transcript = None
    try:
        chunks = YouTubeTranscriptApi.get_transcript(
            yt_vide_id, languages=["es", "en", "en-GB"]
        )
        transcript = "".join([i["text"] for i in chunks])
    except TranscriptsDisabled as e:
        if data.get("whisperConfirmed") != True:
            await send_message(
                {
                    "action": "message",
                    "msgCode": "useWhisper",
                    "msg": "La transcripcion esta desactivada para este video",
                }
            )
            return None
    except NoTranscriptFound as e:
        if data.get("whisperConfirmed") != True:
            await send_message(
                {
                    "action": "message",
                    "msgCode": "useWhisper",
                    "msg": "No existe una transcripcion en los idiomas aceptados",
                }
            )
            return None
    except Exception as e:
        # This is the crucial part for catching the "no element found" error
        logging.error(
            f"An unexpected error occurred while getting YouTube transcript for {yt_vide_id}: {e}",
            exc_info=True,
        )
        await send_message(
            {
                "action": "message",
                "msgCode": "cantGetTranscript",
                "msg": f"An unexpected error occurred while getting YouTube transcript for {yt_vide_id}: {e}",
            }
        )
        raise

    if transcript is None and data.get("whisperConfirmed") == True:
        transcript = await whisper_transcript(data.get("url"))

    if transcript is None:
        await send_message(
            {
                "action": "message",
                "msgCode": "cantGetTranscript",
                "msg": f"An unexpected error occurred while getting YouTube transcript for {yt_vide_id}: {e}",
            }
        )

    return transcript
