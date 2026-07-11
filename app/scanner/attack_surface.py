# -*- coding: utf-8 -*-

"""
WebShield Scanner - Attack Surface Mapper
Maps the attack surface of a website including endpoints, directories, and resources.
"""

import re
from urllib.parse import urlparse, urljoin
from flask import current_app


class AttackSurfaceMapper:
    """Maps website attack surface including endpoints, directories, and resources."""
    
    def __init__(self):
        """Initialize the attack surface mapper."""
        pass
    
    def analyze(self, pages):
        """
        Analyze pages to map the attack surface.
        
        Args:
            pages: List of crawled page data
            
        Returns:
            dict: Attack surface data
        """
        if not pages:
            return {
                'total_pages': 0,
                'endpoints': [],
                'directories': [],
                'login_pages': [],
                'api_endpoints': [],
                'admin_pages': [],
                'file_types': {},
                'technologies': []
            }
        
        surface = {
            'total_pages': len(pages),
            'endpoints': self._extract_endpoints(pages),
            'directories': self._extract_directories(pages),
            'login_pages': self._find_login_pages(pages),
            'api_endpoints': self._find_api_endpoints(pages),
            'admin_pages': self._find_admin_pages(pages),
            'file_types': self._count_file_types(pages),
            'technologies': self._detect_technologies(pages),
            'forms': self._extract_forms(pages),
            'parameters': self._extract_parameters(pages)
        }
        
        return surface
    
    def _extract_endpoints(self, pages):
        """
        Extract all unique endpoints from pages.
        
        Args:
            pages: List of page data
            
        Returns:
            list: Unique endpoints
        """
        endpoints = set()
        
        for page in pages:
            url = page.get('url', '')
            if url:
                parsed = urlparse(url)
                endpoint = parsed.path or '/'
                endpoints.add(endpoint)
            
            # Add links
            for link in page.get('links', []):
                parsed = urlparse(link)
                endpoint = parsed.path or '/'
                if endpoint and endpoint != '/':
                    endpoints.add(endpoint)
        
        return sorted(list(endpoints))
    
    def _extract_directories(self, pages):
        """
        Extract directories from endpoints.
        
        Args:
            pages: List of page data
            
        Returns:
            list: Unique directories
        """
        directories = set()
        
        endpoints = self._extract_endpoints(pages)
        for endpoint in endpoints:
            parts = endpoint.split('/')
            path = ''
            for i, part in enumerate(parts):
                if part:
                    path += '/' + part
                    if i < len(parts) - 1:
                        directories.add(path + '/')
        
        return sorted(list(directories))
    
    def _find_login_pages(self, pages):
        """
        Find login pages.
        
        Args:
            pages: List of page data
            
        Returns:
            list: Login page URLs
        """
        login_pages = []
        login_patterns = [
            r'login', r'signin', r'sign-in', r'log-in', 
            r'auth', r'authenticate', r'oauth', r'sso'
        ]
        
        for page in pages:
            url = page.get('url', '').lower()
            title = (page.get('title') or '').lower()
            
            # Check URL patterns
            for pattern in login_patterns:
                if re.search(pattern, url) or re.search(pattern, title):
                    login_pages.append(page.get('url'))
                    break
            
            # Check for password fields in forms
            for form in page.get('forms', []):
                if form.get('has_password', False):
                    login_pages.append(page.get('url'))
                    break
        
        return list(set(login_pages))
    
    def _find_api_endpoints(self, pages):
        """
        Find API endpoints.
        
        Args:
            pages: List of page data
            
        Returns:
            list: API endpoint URLs
        """
        api_endpoints = []
        api_patterns = [
            r'/api/', r'/v\d+/', r'/rest/', r'/graphql',
            r'/soap/', r'/rpc/', r'/json/', r'/xmlrpc'
        ]
        
        for page in pages:
            url = page.get('url', '')
            
            # Check URL patterns
            for pattern in api_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    api_endpoints.append(url)
                    break
            
            # Check links for API patterns
            for link in page.get('links', []):
                for pattern in api_patterns:
                    if re.search(pattern, link, re.IGNORECASE):
                        api_endpoints.append(link)
                        break
        
        return list(set(api_endpoints))
    
    def _find_admin_pages(self, pages):
        """
        Find admin pages.
        
        Args:
            pages: List of page data
            
        Returns:
            list: Admin page URLs
        """
        admin_pages = []
        admin_patterns = [
            r'/admin', r'/administrator', r'/cp', r'/dashboard',
            r'/manage', r'/moderator', r'/sys', r'/system',
            r'/wp-admin', r'/wp-login', r'/cpanel'
        ]
        
        for page in pages:
            url = page.get('url', '').lower()
            title = (page.get('title') or '').lower()
            
            for pattern in admin_patterns:
                if re.search(pattern, url) or re.search(pattern, title):
                    admin_pages.append(page.get('url'))
                    break
        
        return list(set(admin_pages))
    
    def _count_file_types(self, pages):
        """
        Count file types found.
        
        Args:
            pages: List of page data
            
        Returns:
            dict: File type counts
        """
        file_types = {}
        
        for page in pages:
            url = page.get('url', '')
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            if '.' in path:
                ext = path.split('.')[-1]
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return file_types
    
    def _detect_technologies(self, pages):
        """
        Detect technologies used on the website.
        
        Args:
            pages: List of page data
            
        Returns:
            list: Detected technologies
        """
        technologies = []
        
        # Check for common CMS and frameworks
        cms_patterns = {
            'WordPress': [r'wp-content', r'wp-includes', r'wordpress', r'wp-json'],
            'Joomla': [r'joomla', r'com_content', r'com_modules'],
            'Drupal': [r'drupal', r'sites/default'],
            'Magento': [r'magento', r'skin/frontend'],
            'Shopify': [r'shopify', r'myshopify'],
            'Laravel': [r'laravel', r'csrf-token', r'_token'],
            'Django': [r'django', r'csrfmiddlewaretoken'],
            'Ruby on Rails': [r'rails', r'authenticity_token'],
            'Node.js': [r'node_modules', r'express'],
            'Angular': [r'ng-app', r'angular'],
            'React': [r'react', r'__REACT_'],
            'Vue.js': [r'vue', r'data-v-'],
            'jQuery': [r'jquery', r'jQuery']
        }
        
        # Check headers for server info
        for page in pages:
            headers = page.get('headers', {})
            server = headers.get('server', '').lower()
            
            if 'nginx' in server:
                technologies.append('Nginx')
            if 'apache' in server:
                technologies.append('Apache')
            if 'iis' in server:
                technologies.append('IIS')
            if 'cloudflare' in str(headers):
                technologies.append('Cloudflare')
            
            # Check HTML for CMS patterns
            html = page.get('html') or ''
            for tech, patterns in cms_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, html, re.IGNORECASE):
                        technologies.append(tech)
                        break
        
        return list(set(technologies))
    
    def _extract_forms(self, pages):
        """
        Extract all forms from pages.
        
        Args:
            pages: List of page data
            
        Returns:
            list: Form data
        """
        forms = []
        for page in pages:
            for form in page.get('forms', []):
                forms.append({
                    'url': page.get('url'),
                    'action': form.get('action'),
                    'method': form.get('method'),
                    'has_password': form.get('has_password', False),
                    'has_file_upload': form.get('has_file_upload', False),
                    'input_count': len(form.get('inputs', []))
                })
        return forms
    
    def _extract_parameters(self, pages):
        """
        Extract URL parameters from pages.
        
        Args:
            pages: List of page data
            
        Returns:
            list: Parameter data
        """
        parameters = {}
        
        for page in pages:
            url = page.get('url', '')
            parsed = urlparse(url)
            if parsed.query:
                for param in parsed.query.split('&'):
                    if '=' in param:
                        key = param.split('=')[0]
                        parameters[key] = parameters.get(key, 0) + 1
        
        return [{'name': k, 'count': v} for k, v in sorted(parameters.items(), key=lambda x: x[1], reverse=True)]
