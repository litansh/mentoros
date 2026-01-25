import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

from backend.core.models import VerificationStatus, Resource

logger = logging.getLogger(__name__)

class VerificationEngine:
    def __init__(self, verification_ttl_days: int = 14):
        self.verification_ttl_days = verification_ttl_days
        # Simple in-memory cache for MVP. In production, use Redis.
        # Key: URL string, Value: (VerificationStatus, timestamp)
        self._cache: Dict[str, tuple[VerificationStatus, datetime]] = {}

    async def verify_url(self, url: str) -> VerificationStatus:
        """
        Verifies a URL exists and is reachable.
        Uses HEAD request first, falls back to GET.
        Checks cache first.
        """
        # 1. Check Cache
        cached = self._cache.get(url)
        if cached:
            status, timestamp = cached
            if datetime.now() - timestamp < timedelta(days=self.verification_ttl_days):
                logger.debug(f"Cache hit for {url}: {status}")
                return status

        # 2. Verify
        status = await self._perform_network_check(url)
        
        # 3. Update Cache
        self._cache[url] = (status, datetime.now())
        return status
    
    async def _perform_network_check(self, url: str) -> VerificationStatus:
        headers = {
            "User-Agent": "MentorOS/1.0 (LinkVerifier; +https://mentoros.ai)"
        }
        timeout = httpx.Timeout(5.0, connect=10.0)
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            try:
                # Try HEAD first
                logger.debug(f"Verifying {url} with HEAD...")
                response = await client.head(url, headers=headers)
                if response.status_code < 400:
                    return VerificationStatus.VERIFIED
                
                # If HEAD fails (some servers block it or 405), try GET with stream
                if response.status_code in [405, 403, 404]: # 404 might be genuine, but sometimes GET works
                     logger.debug(f"HEAD failed ({response.status_code}), trying GET for {url}...")
                     async with client.stream("GET", url, headers=headers) as response:
                        if response.status_code < 400:
                            return VerificationStatus.VERIFIED
                        
            except httpx.RequestError as e:
                logger.warning(f"Verification network error for {url}: {e}")
                return VerificationStatus.FAILED
            except Exception as e:
                logger.error(f"Verification unexpected error for {url}: {e}")
                return VerificationStatus.FAILED
        
        return VerificationStatus.FAILED

    async def verify_resource(self, resource: Resource) -> Resource:
        """
        Updates the verification status of a Resource object in place.
        """
        status = await self.verify_url(str(resource.url))
        resource.verification_status = status
        resource.last_verified_at = datetime.now()
        return resource

    async def batch_verify(self, resources: List[Resource]) -> List[Resource]:
        """
        Verifies a list of resources concurrently.
        """
        tasks = [self.verify_resource(res) for res in resources]
        return await asyncio.gather(*tasks)

# Global singleton or dependency injection candidate
verifier = VerificationEngine()
