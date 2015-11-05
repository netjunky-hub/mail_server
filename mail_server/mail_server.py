# -*- coding: utf-8 -*-

from openerp import models, fields, api

class ir_mail_server(models.Model):
    _inherit = "ir.mail_server"

    is_mass_mailing_server = fields.Boolean(string="Mass Mailing Server", help="Use this mail server for mass mailing.")
    user_id = fields.Many2one('res.users', string="Owner", help="If this is personal mail server choose owner.")
    #to do
    #is_user_mail_server = fields.Boolean(string="Mass Mailing Server", help="Use this mail server for mass mailing.")

    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False):

        #get uid from context
        uid=self.env.context.get('uid')

        #if uid is None get uid from env
        if uid is None:
            uid=self.env.uid

        #if mail server has owner use that mail server
        mail_server = self.search([('user_id', '=', uid)], limit=1)
        if mail_server:
            mail_server_id = mail_server.id

        return super(ir_mail_server, self).send_email(message=message, mail_server_id=mail_server_id, smtp_server=smtp_server, smtp_port=smtp_port,
                   smtp_user=smtp_user, smtp_password=smtp_password, smtp_encryption=smtp_encryption, smtp_debug=smtp_debug)

class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        res = super(MailComposeMessage, self).get_mail_values(cr, uid, wizard, res_ids, context=context)
        if wizard.composition_mode == 'mass_mail' and \
           (wizard.mass_mailing_name or wizard.mass_mailing_id) and \
           wizard.model in [item[0] for item in self.pool['mail.mass_mailing']._get_mailing_model(cr, uid, context=context)]:
            mail_server = self.pool.get('ir.mail_server').search(cr, uid, [('is_mass_mailing_server', '=', 'True')], limit=1)
            for res_id in res_ids:
                res[res_id].update({
                    'mail_server_id': mail_server[0],
                })

        return res

