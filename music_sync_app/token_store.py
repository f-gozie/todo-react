import json
import os
import threading
import logging # New import

logger = logging.getLogger(__name__) # Logger for this module

TOKEN_FILE_PATH = "tokens.json"
_lock = threading.Lock()

def save_tokens(service_name: str, token_data: dict) -> bool:
    with _lock:
        tokens = {}
        try:
            if os.path.exists(TOKEN_FILE_PATH) and os.path.getsize(TOKEN_FILE_PATH) > 0:
                with open(TOKEN_FILE_PATH, 'r') as f:
                    tokens = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading token file {TOKEN_FILE_PATH} before save: {e}. Starting with empty tokens.", exc_info=True)
            tokens = {}

        tokens[service_name.lower()] = token_data

        try:
            with open(TOKEN_FILE_PATH, 'w') as f:
                json.dump(tokens, f, indent=4)
            logger.info(f"Tokens saved for {service_name} to {TOKEN_FILE_PATH}")
            return True
        except IOError as e:
            logger.error(f"Error writing token file {TOKEN_FILE_PATH}: {e}", exc_info=True)
            return False

def load_tokens(service_name: str) -> dict | None:
    with _lock:
        if not os.path.exists(TOKEN_FILE_PATH):
            # logger.debug(f"Token file {TOKEN_FILE_PATH} not found.") # Can be too verbose
            return None
        try:
            with open(TOKEN_FILE_PATH, 'r') as f:
                tokens = json.load(f)
            return tokens.get(service_name.lower())
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading or parsing token file {TOKEN_FILE_PATH}: {e}", exc_info=True)
            return None

def delete_tokens(service_name: str) -> bool:
    with _lock:
        tokens = {}
        if not os.path.exists(TOKEN_FILE_PATH):
            logger.info(f"Token file {TOKEN_FILE_PATH} not found. Nothing to delete for {service_name}.")
            return True

        try:
            if os.path.getsize(TOKEN_FILE_PATH) > 0:
                 with open(TOKEN_FILE_PATH, 'r') as f:
                    tokens = json.load(f)

            if service_name.lower() in tokens:
                del tokens[service_name.lower()]
                try:
                    with open(TOKEN_FILE_PATH, 'w') as f:
                        json.dump(tokens, f, indent=4)
                    logger.info(f"Tokens deleted for {service_name} from {TOKEN_FILE_PATH}")
                    return True
                except IOError as e:
                    logger.error(f"Error writing token file after deleting {service_name}: {e}", exc_info=True)
                    return False
            else:
                logger.info(f"No tokens found for {service_name} to delete.")
                return True
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading token file {TOKEN_FILE_PATH} during delete: {e}", exc_info=True)
            return False

def load_all_tokens() -> dict:
    with _lock:
        if not os.path.exists(TOKEN_FILE_PATH):
            return {}
        try:
            with open(TOKEN_FILE_PATH, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading all tokens from {TOKEN_FILE_PATH}: {e}", exc_info=True)
            return {}


if __name__ == '__main__':
    # Setup basic logging for standalone test if needed
    if not logging.getLogger().hasHandlers(): # Check if logging is already configured
        from logging_config import setup_logging # Assuming logging_config is in the same dir for test
        setup_logging(debug_mode=True)

    logger.info("Token Store Module - Standalone Test")

    test_spotify_token = {"access_token": "spotify_test_access", "refresh_token": "spotify_test_refresh", "expires_at": 12345}
    test_deezer_token = {"access_token": "deezer_test_access", "expires": 3600}
    test_youtube_creds = {"credentials_json": json.dumps({"client_id": "yt_test_client", "token": "yt_test_token"})}

    logger.info(f"Saving Spotify tokens: {save_tokens('spotify', test_spotify_token)}")
    loaded_sp = load_tokens('spotify')
    logger.info(f"Loaded Spotify: {loaded_sp}")
    assert loaded_sp == test_spotify_token

    logger.info(f"Saving Deezer tokens: {save_tokens('deezer', test_deezer_token)}")
    loaded_dz = load_tokens('deezer')
    logger.info(f"Loaded Deezer: {loaded_dz}")
    assert loaded_dz == test_deezer_token

    logger.info(f"Saving YouTube tokens: {save_tokens('youtube', test_youtube_creds)}")
    loaded_yt = load_tokens('youtube')
    logger.info(f"Loaded YouTube: {loaded_yt}")
    assert loaded_yt == test_youtube_creds

    all_loaded = load_all_tokens()
    logger.info(f"All loaded: {all_loaded}")
    assert "spotify" in all_loaded and "deezer" in all_loaded and "youtube" in all_loaded

    logger.info(f"Deleting Spotify tokens: {delete_tokens('spotify')}")
    assert load_tokens('spotify') is None
    all_loaded_after_delete = load_all_tokens()
    logger.info(f"All loaded after delete: {all_loaded_after_delete}")
    assert "spotify" not in all_loaded_after_delete

    if os.path.exists(TOKEN_FILE_PATH):
        os.remove(TOKEN_FILE_PATH)
    logger.info(f"Cleaned up {TOKEN_FILE_PATH}")
