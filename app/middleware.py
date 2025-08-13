"""
Middleware components for the AI Avatar Video application.
"""

import os
import time
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional

logger = logging.getLogger("ai-avatar-video")

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses with timing information."""
    
    async def dispatch(self, request: Request, call_next):
        # Get request details
        request_id = request.headers.get("X-Request-ID", "")
        start_time = time.time()
        
        # Log the request
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"(ID: {request_id}) - Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        # Process the request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log the response
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"(ID: {request_id}) - Status: {response.status_code} - Time: {process_time:.3f}s"
            )
            
            # Add timing header
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"(ID: {request_id}) - Error: {str(e)} - Time: {process_time:.3f}s"
            )
            raise

def add_middleware(app: FastAPI) -> None:
    """Add custom middleware to the FastAPI application."""
    app.add_middleware(LoggingMiddleware)
    
    # Add IP whitelist middleware if config file exists
    ip_config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "allowed_ips.conf")
    if os.path.exists(ip_config_file):
        app.add_middleware(IPWhitelistMiddleware, config_file=ip_config_file)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Middleware to restrict access to specific IP addresses."""
    
    def __init__(
        self, 
        app: FastAPI, 
        whitelisted_ips: Optional[List[str]] = None,
        config_file: Optional[str] = None,
        enabled: bool = True
    ):
        """Initialize the middleware.
        
        Args:
            app: The FastAPI application
            whitelisted_ips: List of allowed IP addresses
            config_file: Path to a configuration file containing allowed IPs (one per line)
            enabled: Whether the middleware is enabled
        """
        super().__init__(app)
        self.enabled = enabled
        self.whitelisted_ips = whitelisted_ips or []
        
        # Load IPs from config file if provided
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        self.whitelisted_ips.append(line)
            logger.info(f"Loaded {len(self.whitelisted_ips)} IP addresses from whitelist")
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and enforce IP restrictions."""
        # Disable IP whitelist for development mode
        development_mode = os.environ.get("DEVELOPMENT_MODE", "false").lower() == "true"
        if development_mode:
            return await call_next(request)
            
        if not self.enabled or not self.whitelisted_ips:
            return await call_next(request)
        
        # Get the client's IP address
        client_ip = request.client.host if request.client else None
        
        # Always allow localhost
        if client_ip in ['127.0.0.1', 'localhost', '::1']:
            return await call_next(request)
        
        # Always allow WebSocket connections (necessary for React Native development)
        if request.url.path.startswith('/message') or request.url.path.startswith('/inspector'):
            return await call_next(request)
        
        # Check if the client's IP is in the whitelist
        if client_ip not in self.whitelisted_ips:
            logger.warning(f"Access denied for IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied. Your IP is not allowed."}
            )
        
        # IP is allowed, proceed with the request
        return await call_next(request)
