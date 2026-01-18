class ForceSecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # CSP POLICY
        # 1. script-src/style-src: Allows Bootstrap CDN
        # 2. font-src: FIXED to allow Bootstrap Icons (cdn.jsdelivr.net)
        # 3. connect-src: Added to allow map files
        
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:; "
            "img-src 'self' data:; "
            "connect-src 'self' https://cdn.jsdelivr.net;"
        )
        
        response['Content-Security-Policy'] = csp_policy
        return response