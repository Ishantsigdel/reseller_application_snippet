from odoo import http
from odoo.http import request
import json

class ResellerController(http.Controller):
    
    @http.route('/reseller/apply', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def submit_reseller_application(self, **kwargs):
        
        try:
            name = kwargs.get('name', '').strip()
            email = kwargs.get('email', '').strip()
            phone = kwargs.get('phone', '').strip()
            company_name = kwargs.get('company_name', '').strip()
            reason = kwargs.get('reason', '').strip()
            
            if not name or not email:
                return json.dumps({
                    'success': False,
                    'message': 'Please enter both name and email'
                })
            
            existing_application = request.env['reseller.application'].sudo().search([
                ('email', '=', email)
            ], limit=1)
            
            if existing_application:
                return json.dumps({
                    'success': False,
                    'message': 'An application with this email already exists.'
                })
            
            application_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'company_name': company_name,
                'reason': reason,
                'state': 'submitted'
            }

            request.env['reseller.application'].sudo().create(application_data)
            
            return json.dumps({
                'success': True,
                'message': 'Your reseller application has been submitted successfully! We will review it and get back to you.'
            })
            
        except Exception as e:
            return json.dumps({
                'success': False,
                'message': 'Error occurred while submitting your application.'
            })
    
    @http.route('/reseller/check', type='json', auth='public', methods=['POST'], website=True)
    def check_existing_application(self, **kwargs):
        
        email = kwargs.get('email', '').strip()
        
        if not email:
            return {'exists': False}
        
        existing = request.env['reseller.application'].sudo().search([
            ('email', '=', email)
        ], limit=1)
        
        return {
            'exists': bool(existing),
            'status': existing.state if existing else None
        }
    
    @http.route('/my/reseller', type='http', auth='user', website=True)
    def reseller_portal_dashboard(self, **kwargs):
        """Portal dashboard for approved resellers"""
        user = request.env.user
        
        # Check if user is a reseller
        reseller_app = request.env['reseller.application'].sudo().search([
            ('user_id', '=', user.id),
            ('state', '=', 'approved')
        ], limit=1)
        
        if not reseller_app:
            return request.render('website.404')
        
        values = {
            'reseller_app': reseller_app,
            'user': user,
            'partner': user.partner_id,
        }
        
        return request.render('reseller_application.portal_dashboard', values)