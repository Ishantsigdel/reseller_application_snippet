from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class ResellerApplication(models.Model):
    _name = "reseller.application"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _description = "Reseller Application"

    send_approval_email = fields.Boolean("Send Approval Email", default=False)

    name = fields.Char("Full Name", required=True)
    email = fields.Char("Email", required=True)
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
    )
    application_date = fields.Datetime("Application Date", default=fields.Datetime.now)

    partner_id = fields.Many2one("res.partner", string="Partner", readonly=True)
    user_id = fields.Many2one("res.users", string="Portal User", readonly=True)
    rejection_reason = fields.Text("Rejection Reason")
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_date = fields.Datetime("Approved Date", readonly=True)

    def action_approve(self):
        for record in self:
            if record.state != "submitted":
                continue

            # Create partner
            partner = record._create_partner()

            # Create portal user
            user = record._create_portal_user(partner)

            # Update record with all the necessary information
            record.write(
                {
                    "state": "approved",
                    "partner_id": partner.id,
                    "user_id": user.id,
                    "approved_by": self.env.user.id,
                    "approved_date": fields.Datetime.now(),
                }
            )

            # Log the approval with multiple access options
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            # import pdb; pdb.set_trace()
            portal_url = f"{base_url}/my"

            if record.send_approval_email:
                record._send_approval_email(user)
            else:
                record.message_post(
                    body=f"Reseller application approved.<br/>"
                    f"Portal user created: <strong>{user.login}</strong><br/>"
                    f"<a href='{portal_url}' target='_blank'>Open Portal (New Tab)</a><br/>"
                    f"User ID: {user.id} | Partner ID: {partner.id}<br/>"
                    f"(No email sent)",
                    message_type="notification",
                )

    def action_reject(self):
        for record in self:
            if record.state != "submitted":
                continue
            record.write(
                {
                    "state": "rejected",
                    "approved_by": self.env.user.id,
                    "approved_date": fields.Datetime.now(),
                }
            )

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
            # Don't set password - user will need to reset it manually
            # 'password': False  # or omit this field entirely
        }

        user = self.env["res.users"].create(user_data)

        # Optionally, prepare signup token for later use
        partner.signup_prepare()

        return user

    def action_impersonate_user(self):
        """Allow admin to impersonate this portal user"""
        if not self.user_id:
            raise UserError(
                "No portal user created yet. Please approve the application first."
            )

        # Switch to portal user context
        return {
            "type": "ir.actions.act_window",
            "name": "Portal Dashboard",
            "res_model": "portal.mixin",
            "view_mode": "form",
            "target": "main",
            "context": {"switch_to_user_id": self.user_id.id},
        }

    # def action_preview_portal(self):
    #     """Allow admin to preview portal as this user"""
    #     if not self.user_id:
    #         raise UserError(
    #             "No portal user created yet. Please approve the application first."
    #         )

    #     base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

    #     # Generate a one-time access token for admin preview
    #     portal_url = f"{base_url}/my?preview_user={self.user_id.id}"

    #     return {
    #         "type": "ir.actions.act_url",
    #         "url": portal_url,
    #         "target": "new",
    #     }

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

    # def _send_approval_email(self, user):
    #     """Send approval email to the applicant"""
    #     try:
    #         email_values = {
    #             "subject": "Your Reseller Application is Approved!",
    #             "body_html": f"""
    #                 <p>Hello <strong>{self.name}</strong>,</p>
    #                 <p>Great news! Your reseller application has been approved.</p>
    #                 <p>You can now access your reseller portal at: <a href="/my/reseller">Login Here</a></p>
    #                 <p>Your login email: {self.email}</p>
    #                 <p>Thank you for joining our reseller network!</p>
    #             """,
    #             "email_to": self.email,
    #             "email_from": self.env.user.email,
    #         }

    #         mail = self.env["mail.mail"].create(email_values)
    #         mail.send()

    #         self.message_post(
    #             body="Approval email sent to %s" % self.email,
    #             message_type="notification",
    #         )

    #     except Exception as e:
    #         self.message_post(
    #             body="Approved but email failed: %s" % str(e),
    #             message_type="notification",
    #         )
