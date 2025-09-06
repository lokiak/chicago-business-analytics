
import time
import requests
import logging
import sys
from pathlib import Path

# Add path for security utilities
sys.path.append(str(Path(__file__).parent.parent / "shared"))
from security_utils import rate_limit, InputValidator, SecurityLogger, SecurityError

DEFAULT_LIMIT = 50000

class SocrataClient:
    def __init__(self, domain: str):
        self.base = f"https://{domain}/resource"
        self.logger = logging.getLogger("market_radar")

    @rate_limit(calls_per_second=1.0)  # Rate limit API calls
    def get(self, dataset_id: str, params, limit: int = DEFAULT_LIMIT, retries: int = 3, backoff: float = 1.5, dataset_name: str = None):
        out, offset = [], 0
        while True:
            p = dict(params)
            p["$limit"] = min(limit, DEFAULT_LIMIT)
            p["$offset"] = offset
            url = f"{self.base}/{dataset_id}.json"

            self.logger.info(f"Requesting data from {url} with params: {p}")

            for attempt in range(retries):
                try:
                    self.logger.info(f"Attempt {attempt + 1}/{retries} for offset {offset}")
                    r = requests.get(url, params=p, timeout=60)

                    self.logger.info(f"Response status: {r.status_code}")
                    self.logger.info(f"Response headers: {dict(r.headers)}")

                    if r.status_code == 200:
                        try:
                            chunk = r.json()
                            self.logger.info(f"Successfully parsed JSON response with {len(chunk)} records")
                            
                            # Log API call for security monitoring
                            SecurityLogger.log_api_call(url, r.status_code, len(r.text))
                            
                            # Validate the response data if dataset name is provided
                            if dataset_name and chunk:
                                try:
                                    InputValidator.validate_api_response(chunk, dataset_name)
                                except SecurityError as e:
                                    self.logger.error(f"Security validation failed: {e}")
                                    SecurityLogger.log_security_event("validation_failure", f"Dataset: {dataset_name}, Error: {e}", "WARNING")
                                    # Continue processing but log the issue
                            
                            out.extend(chunk)
                            break
                        except ValueError as e:
                            self.logger.error(f"Failed to parse JSON response: {e}")
                            self.logger.error(f"Response content (first 500 chars): {r.text[:500]}")
                            SecurityLogger.log_api_call(url, r.status_code, 0)  # Log failed parse
                            if attempt == retries - 1:
                                raise RuntimeError(f"Failed to parse JSON response after {retries} attempts: {e}")
                    else:
                        self.logger.error(f"HTTP {r.status_code} error for attempt {attempt + 1}")
                        self.logger.error(f"Response content: {r.text}")

                        if attempt == retries - 1:
                            raise RuntimeError(
                                f"Failed Socrata request after {retries} retries. "
                                f"URL: {url}, Status: {r.status_code}, "
                                f"Response: {r.text[:200]}"
                            )

                    # Wait before retry
                    if attempt < retries - 1:
                        wait_time = backoff * (attempt + 1)
                        self.logger.info(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)

                except requests.exceptions.RequestException as e:
                    self.logger.error(f"Request exception on attempt {attempt + 1}: {e}")
                    if attempt == retries - 1:
                        raise RuntimeError(
                            f"Failed Socrata request after {retries} retries due to request exception: {e}. "
                            f"URL: {url}"
                        )
                    # Wait before retry
                    wait_time = backoff * (attempt + 1)
                    self.logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)

            if len(chunk) < p["$limit"]:
                self.logger.info(f"Received {len(chunk)} records (less than limit {p['$limit']}), ending pagination")
                break
            offset += p["$limit"]
            self.logger.info(f"Moving to next page, new offset: {offset}")

        self.logger.info(f"Total records fetched: {len(out)}")
        return out
