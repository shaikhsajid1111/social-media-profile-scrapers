from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class HTTPSettings:
    timeout: int = 60
    retry: int = 3
    
    # field(default_factory=dict) ensures EVERY instance gets its own clean copy
    query: Dict[str, str] = field(default_factory=dict)
    
    # Headers must hold anti-bot footprints like Sec-Ch-Ua, Accept-Language, etc.
    headers: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    # Crucial for scraping locked down content or managing logins
    cookies: Dict[str, str] = field(default_factory=dict)
    
    # Format: {"http": "http://user:pass@ip:port", "https": "http://user:pass@ip:port"}
    proxies: Optional[Dict[str, str]] = None
