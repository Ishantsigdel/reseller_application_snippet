from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import re  


class ResellerApplication(models.Model):
    _name = "reseller.application"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _description = "Reseller Application"

    send_approval_email = fields.Boolean("Send Approval Email", default=False)

    name = fields.Char("Full Name", required=True, tracking=True)
    email = fields.Char("Email", required=True, tracking=True)
    phone = fields.Char("Phone Number")
    company_name = fields.Char("Company Name")
    reason = fields.Text("Reason for Applying")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        string="Status",
        tracking=True,
    )
    application_date = fields.Datetime("Application Date", default=fields.Datetime.now)

    partner_id = fields.Many2one("res.partner", string="Partner", readonly=True)
    user_id = fields.Many2one("res.users", string="Portal User", readonly=True)
    rejection_reason = fields.Text("Rejection Reason")
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_date = fields.Datetime("Approved Date", readonly=True)

    @api.constrains('email')
    def _check_email_format(self):
        for record in self:
            if record.email and '@' not in record.email:
                raise ValidationError("Email must contain '@' symbol.")
            
            if record.email:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, record.email):
                    raise ValidationError("Please enter a valid email address.")

    @api.constrains('phone')
    def _check_phone_format(self):
        for record in self:
            if record.phone:
                if not any(char.isdigit() for char in record.phone):
                    raise ValidationError("Phone number must contain at least one digit.")
                
                if record.phone.isalpha():
                    raise ValidationError("Phone number cannot contain only letters.")

    def action_submit(self):
        """Submit application with validation and notification"""
        for record in self:
            # Validate required fields
            if not record.email or not record.phone:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Missing Required Fields',
                        'message': 'Email and Phone are required to submit the application.',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
            
            # Email validation
            if '@' not in record.email:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Invalid Email',
                        'message': 'Email must contain "@" symbol to submit the application.',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
            
            # Phone validation
            if not any(char.isdigit() for char in record.phone):
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Invalid Phone',
                        'message': 'Phone number must contain at least one digit.',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
            
            # Update state
            record.state = 'submitted'
            record.message_post(body="Application submitted for review.")
            
            # Success notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success!',
                    'message': f'Application for {record.name} has been submitted successfully.',
                    'type': 'success',
                    'sticky': False,
                }
            }

    def action_approve(self):
        """Approve application with notification"""
        for record in self:
            if record.state != "submitted":
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Action Not Allowed',
                        'message': 'Only submitted applications can be approved.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }
            
            partner = record._create_partner()
            user = record._create_portal_user(partner)
            
            # Update record with all the necessary information
            record.write({
                "state": "approved",
                "partner_id": partner.id,
                "user_id": user.id,
                "approved_by": self.env.user.id,
                "approved_date": fields.Datetime.now(),
            })
            
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            portal_url = f"{base_url}/my"
            
            if record.send_approval_email:
                record._send_approval_email(user)
            else:
                record.message_post(
                    body=f"Reseller application approved. "
                        f"Portal user created: **{user.login}** "
                        f"<a href='{portal_url}' target='_blank' class='btn btn-primary btn-sm'>Open Portal (New Tab)</a> "
                        f"User ID: {user.id} | Partner ID: {partner.id} "
                        f"(No email sent)",
                    message_type="notification",
                )
            
            # Return action to reload the current view and show notification
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                'params': {
                    'notification': {
                        'title': 'Application Approved!',
                        'message': f'Reseller application for {record.name} has been approved successfully. Portal user created.',
                        'type': 'success',
                    }
                }
            }

    def action_reject(self):
        """Reject application with notification"""
        for record in self:
            if record.state != "submitted":
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Action Not Allowed',
                        'message': 'Only submitted applications can be rejected.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }
            
            record.write(
                {
                    "state": "rejected",
                    "approved_by": self.env.user.id,
                    "approved_date": fields.Datetime.now(),
                }
            )

            # Post message to chatter
            record.message_post(
                body=f"Application rejected. Reason: {record.rejection_reason or 'No reason provided'}",
                message_type="notification",
            )

            # Rejection notification
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Application Rejected',
                    'message': f'Application for {record.name} has been rejected.',
                    'type': 'danger',
                    'sticky': False,
                }
            }

    def action_reset_to_draft(self):
        """Reset application to draft state"""
        for record in self:
            record.state = 'draft'
            record.message_post(body="Application reset to draft.")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Reset to Draft',
                    'message': f'Application for {record.name} has been reset to draft state.',
                    'type': 'info',
                    'sticky': False,
                }
            }

    def _create_partner(self):
        partner_data = {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "is_company": bool(self.company_name),
            "comment": f"Reseller Application: {self.reason}",
        }

        if self.company_name:
            partner_data["name"] = self.company_name

        return self.env["res.partner"].create(partner_data)

    def _create_portal_user(self, partner):
        portal_group = self.env.ref("base.group_portal")

        user_data = {
            "name": self.name,
            "login": self.email,
            "email": self.email,
            "partner_id": partner.id,
            "groups_id": [(6, 0, [portal_group.id])],
            "active": True,
        }

        user = self.env["res.users"].create(user_data)
        partner.signup_prepare()

        return user

    def action_impersonate_user(self):
        if not self.user_id:
            raise UserError(
                "No portal user created yet. Please approve the application first."
            )

        return {
            "type": "ir.actions.act_window",
            "name": "Portal Dashboard",
            "res_model": "portal.mixin",
            "view_mode": "form",
            "target": "main",
            "context": {"switch_to_user_id": self.user_id.id},
        }

    def action_open_user_record(self):
        """Open the created portal user record"""
        if not self.user_id:
            raise UserError("No portal user created yet.")

        return {
            "type": "ir.actions.act_window",
            "res_model": "res.users",
            "res_id": self.user_id.id,
            "view_mode": "form",
            "target": "new",
        }