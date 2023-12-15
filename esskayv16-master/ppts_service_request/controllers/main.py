# -*- coding: utf-8 -*-
from datetime import date

from odoo import http
from odoo.http import request, Response
import requests
import base64
import json, werkzeug


class ServiceRequestWebsiteForm(http.Controller):

    # Stryker
    @http.route(['/stryker_request'], type='http', auth="public", website=True)
    def Strykerrequest(self, **kw):
        website_company_id = request.website
        service_category_ids = request.env['service.category'].sudo().search([])
        service_type_ids = request.env['service.type'].sudo().search([])
        customer_state_ids = request.env['res.country.state'].sudo().search([])
        customer_country_ids = request.env['res.country'].sudo().search([])
        customer_city_ids = request.env['res.city'].sudo().search([])
        customer_region_ids = request.env['customer.region'].sudo().search([('active', '=', True)])
        customer_type_ids = request.env['customer.type'].sudo().search([('active', '=', True)])
        case_completed_successfully_ids = request.env['case.completed.successfully'].sudo().search([])
        medical_intervention_ids = request.env['medical.intervention'].sudo().search([])
        patient_involved_ids = request.env['patient.involved'].sudo().search([])
        surgical_delay_ids = request.env['surgical.delay'].sudo().search([])
        custom_serial_no = kw.get('custom_product_serial')
        serial_no_sear = request.env['product.product'].sudo().search([('name', '=', custom_serial_no)], limit=1)
        def_country_id = request.env['res.country'].search([('code', '=', 'IN')], limit=1)
        values = {
            'service_category_ids': service_category_ids,
            'customer_state_ids': customer_state_ids,
            'customer_country_ids': customer_country_ids,
            'customer_city_ids': customer_city_ids,
            'customer_region_ids': customer_region_ids,
            'service_type_ids': service_type_ids,
            'customer_type_ids': customer_type_ids,
            'case_completed_successfully_ids': case_completed_successfully_ids,
            'medical_intervention_ids': medical_intervention_ids,
            'patient_involved_ids': patient_involved_ids,
            'surgical_delay_ids': surgical_delay_ids,
            'def_country': def_country_id,
            'current_url': str(http.request.httprequest.full_path).replace('?', ''),
        }
        return request.render("ppts_service_request.create_stryker_request", values)

    @http.route(['/update_state_id'], type='json', auth="public", website=True, methods=['POST'])
    def update_sales_note(self, country):
        list_state = []
        states = request.env['res.country.state'].sudo().search([('country_id', '=', int(country))])
        for state in states:
            list_state.append({
                'id': state.id,
                'value': state.name
            })
        return {'state_domain': list_state}

    @http.route(['/create/strykerrequest/fsm'], type='http', auth="public", methods=['POST'], website=True)
    def create_request_fsm(self, **kw):
        ticket_type = kw.get('ticket_type')
        if ticket_type == 'stryker_fsm':
            fsm_id = request.env['request.type'].sudo().search([('ticket_type', '=', 'sr_fsm')], limit=1)
            company = request.env['res.company'].sudo().search([('website_menu_id.url', '=', kw.get('current_url'))],
                                                               limit=1)
            team_id = request.env['crm.team'].sudo().search(
                [('customer_type', '=', 'stryker'), ('company_id', '=', company.id)], limit=1)
            stryker_request_vals = {
                'request_type_id': fsm_id.id,
                'team_id': team_id.id,
                'company_id': company.id,
                'customer_name': kw.get('customer_name'),
                # 'requested_by_name' : kw.get('requested_by_name'),
                'requested_by_contact_number': kw.get('requested_by_contact_number'),
                'customer_email': kw.get('customer_email'),
                'customer_region_id': kw.get('customer_region_id'),
                'customer_street': kw.get('customer_street'),
                'customer_street2': kw.get('customer_street2'),
                'customer_city_id': kw.get('customer_city_id'),
                'customer_state_id': kw.get('customer_state_id'),
                'customer_zip': kw.get('customer_zip'),
                'customer_country_id': kw.get('customer_country_id'),
                'service_category_id': kw.get('service_category_id'),
                'model': kw.get('model'),
                'custom_product_serial': kw.get('custom_product_serial'),
                'remarks': kw.get('description'),
                'event_date': kw.get('event_date') or False,
                'issue_noticed': kw.get('issue_noticed'),
                'case_completed_successfully_id': kw.get('case_completed_id'),
                'medical_intervention_id': kw.get('medical_intervention_id'),
                'patient_involved_id': kw.get('patient_involved_id'),
                'surgical_delay_id': kw.get('surgical_delay_id'),
                'select_adverse_consequences': kw.get('adverse_consequences'),
                'is_website_order': True,
                'hospital_name': kw.get('hospital_name'),
                'product_part_code': kw.get('product_part_code'),
                'service_request_date': date.today(),
            }
        stryker_records = request.env['service.request'].sudo().create(stryker_request_vals)
        if request.env.user.has_group('ppts_service_request.service_request_group_user'):
            stryker_records.action_submit()
        teams = request.env['crm.team'].sudo().search([('customer_type', '=', 'stryker')])
        mail_list = []
        for members in teams.member_ids:
            if members.has_group('ppts_service_request.service_request_group_ct_user'):
                mail_list.append(members.login)
        mails = ', '.join(mail_list)
        template_id = request.env.ref('ppts_service_request.email_template_stryker_request')
        if ticket_type == 'stryker_fsm':
            action_id = request.env.ref('ppts_service_request.action_service_request_sr_fsm')
        else:
            action_id = request.env.ref('ppts_service_request.action_service_request')
        base_url = '/web#id=%d&action=%r&model=service.request&view_type=form' % (stryker_records.id, action_id.id)

        if template_id:
            template_id.with_context(email_to=mails, rec_url=base_url).sudo().send_mail(stryker_records.id,
                                                                                        force_send=True)
        values = {'stryker_records': stryker_records}
        if 'attachment' in request.params:
            attachment_list = request.httprequest.files.getlist('attachment')
            for image in attachment_list:
                if kw.get('attachment'):
                    attachments = {
                        'res_name': image.filename,
                        'res_model': 'service.request',
                        'res_id': stryker_records.id,
                        'datas': base64.encodestring(image.read()),
                        'type': 'binary',
                        # 'datas_fname': image.filename,
                        'name': image.filename,
                    }
                    attachment_obj = http.request.env['ir.attachment']
                    attachments_vals = attachment_obj.sudo().create(attachments)
                    stryker_records.update({
                        'attachment_ids': [(4, attachments_vals.id)],
                    })

        return request.render("ppts_service_request.stryker_request_thanks", values)

    @http.route(['/create/strykerrequest/installation'], type='http', auth="public", methods=['POST'], website=True)
    def create_request_installation(self, **kw):
        ticket_type = kw.get('ticket_type')
        if ticket_type == 'stryker_installation':
            installation_id = request.env['request.type'].sudo().search([('ticket_type', '=', 'sr_installation')],
                                                                        limit=1)
            company = request.env['res.company'].sudo().search([('website_menu_id.url', '=', kw.get('current_url'))],
                                                               limit=1)
            team_id = request.env['crm.team'].sudo().search(
                [('customer_type', '=', 'stryker'), ('company_id', '=', company.id)], limit=1)
            stryker_request_vals = {
                'request_type_id': installation_id.id,
                'team_id': team_id.id,
                'company_id': company.id,
                'customer_name': kw.get('customer_name'),
                # 'requested_by_name' : kw.get('requested_by_name'),
                'requested_by_contact_number': kw.get('requested_by_contact_number'),
                'customer_email': kw.get('customer_email'),
                'customer_region_id': kw.get('customer_region_id'),
                'customer_street': kw.get('customer_street'),
                'customer_street2': kw.get('customer_street2'),
                'customer_city_id': kw.get('customer_city_id'),
                'customer_state_id': kw.get('sr_inst_state_id'),
                'customer_zip': kw.get('customer_zip'),
                'customer_country_id': kw.get('sr_inst_country_id'),
                'install_addr_street': kw.get('installation_location'),
                'location_contact_person': kw.get('location_contact_person'),
                'installation_date': kw.get('installation_date') or False,
                'service_type_id': kw.get('service_type_id'),
                'service_category_id': kw.get('service_category_id'),
                'customer_type_id': kw.get('customer_type_id'),
                'customer_po_number': kw.get('customer_po_no'),
                'customer_po_date': kw.get('customer_po_date') or False,
                'invoice_number': kw.get('invoice_no'),
                'invoice_date': kw.get('invoice_date') or False,
                'tender_refer_number': kw.get('tender_reference_no'),
                'extended_invoice_number': kw.get('extended_warranty_invoice_no'),
                'extended_invoice_date': kw.get('extended_warranty_invoice_date') or False,
                'is_website_order': True,
                'hospital_name': kw.get('hospital_name'),
                'product_part_code': kw.get('product_part_code'),
                'service_request_date': date.today(),
            }

        stryker_records = request.env['service.request'].sudo().create(stryker_request_vals)
        if request.env.user.has_group('ppts_service_request.service_request_group_user'):
            stryker_records.action_submit()
        teams = request.env['crm.team'].sudo().search([('customer_type', '=', 'stryker')])
        mail_list = []
        for members in teams.member_ids:
            if members.has_group('ppts_service_request.service_request_group_ct_user'):
                mail_list.append(members.login)
        mails = ', '.join(mail_list)
        template_id = request.env.ref('ppts_service_request.email_template_stryker_request')
        if ticket_type == 'stryker_installation':
            action_id = request.env.ref('ppts_service_request.action_service_request_sr_installation')
        else:
            action_id = request.env.ref('ppts_service_request.action_service_request')
        base_url = '/web#id=%d&action=%r&model=service.request&view_type=form' % (stryker_records.id, action_id.id)

        if template_id:
            template_id.with_context(email_to=mails, rec_url=base_url).sudo().send_mail(stryker_records.id,
                                                                                        force_send=True)
        values = {'stryker_records': stryker_records}
        if 'attachment' in request.params:
            attachment_list = request.httprequest.files.getlist('attachment')
            for image in attachment_list:
                if kw.get('attachment'):
                    attachments = {
                        'res_name': image.filename,
                        'res_model': 'service.request',
                        'res_id': stryker_records.id,
                        'datas': base64.encodestring(image.read()),
                        'type': 'binary',
                        # 'datas_fname': image.filename,
                        'name': image.filename,
                    }
                    attachment_obj = http.request.env['ir.attachment']
                    attachments_vals = attachment_obj.sudo().create(attachments)
                    stryker_records.update({
                        'attachment_ids': [(4, attachments_vals.id)],
                    })

        return request.render("ppts_service_request.stryker_request_thanks", values)

    # thermofisher
    @http.route(['/thermofisher_request'], type='http', auth="public", website=True)
    def thermofisherrequest(self, **kw):
        website_company_id = request.website
        service_category_ids = request.env['service.category'].sudo().search([])
        service_type_ids = request.env['service.type'].sudo().search([])
        customer_state_ids = request.env['res.country.state'].sudo().search([])
        customer_country_ids = request.env['res.country'].sudo().search([])
        customer_city_ids = request.env['res.city'].sudo().search([])
        customer_region_ids = request.env['customer.region'].sudo().search([('active', '=', True)])
        customer_type_ids = request.env['customer.type'].sudo().search([('active', '=', True)])
        case_completed_successfully_ids = request.env['case.completed.successfully'].sudo().search([])
        medical_intervention_ids = request.env['medical.intervention'].sudo().search([])
        patient_involved_ids = request.env['patient.involved'].sudo().search([])
        surgical_delay_ids = request.env['surgical.delay'].sudo().search([])
        custom_serial_no = kw.get('custom_product_serial')
        serial_no_sear = request.env['product.product'].sudo().search([('name', '=', custom_serial_no)], limit=1)
        values = {
            'service_category_ids': service_category_ids,
            'customer_state_ids': customer_state_ids,
            'customer_country_ids': customer_country_ids,
            'customer_city_ids': customer_city_ids,
            'customer_region_ids': customer_region_ids,
            'service_type_ids': service_type_ids,
            'customer_type_ids': customer_type_ids,
            'case_completed_successfully_ids': case_completed_successfully_ids,
            'medical_intervention_ids': medical_intervention_ids,
            'patient_involved_ids': patient_involved_ids,
            'surgical_delay_ids': surgical_delay_ids,
        }
        return request.render("ppts_service_request.create_thermofisher_request", values)

    @http.route(['/create/thermofisherrequest/fsm'], type='http', auth="public", methods=['POST'], website=True)
    def create_thermofisher_request_fsm(self, **kw):
        ticket_type = kw.get('ticket_type')
        if ticket_type == 'thermofisher_fsm':
            fsm_id = request.env['request.type'].sudo().search([('ticket_type', '=', 'sr_fsm')], limit=1)
            team_id = request.env['crm.team'].sudo().search([('customer_type', '=', 'termo_fisher')], limit=1)
            thermofisher_request_vals = {
                'request_type_id': fsm_id.id,
                'team_id': team_id.id,
                'requested_by_name': kw.get('customer_name'),
                'customer_name': kw.get('requested_by_name'),
                'requested_by_contact_number': kw.get('requested_by_contact_number'),
                'customer_email': kw.get('customer_email'),
                'customer_region_id': kw.get('customer_region_id'),
                'customer_street': kw.get('customer_street'),
                'customer_street2': kw.get('customer_street2'),
                'customer_city_id': kw.get('customer_city_id'),
                'customer_state_id': kw.get('customer_state_id'),
                'customer_zip': kw.get('customer_zip'),
                'customer_country_id': kw.get('customer_country_id'),
                'service_category_id': kw.get('service_category_id'),
                'model': kw.get('model'),
                'custom_product_serial': kw.get('custom_product_serial'),
                'remarks': kw.get('description'),
                'is_website_order': True,
                'product_part_code': kw.get('product_part_code'),
                'service_request_date': date.today(),
            }
        thermofisher_records = request.env['service.request'].sudo().create(thermofisher_request_vals)
        if request.env.user.has_group('ppts_service_request.service_request_group_user'):
            thermofisher_records.action_submit()
        teams = request.env['crm.team'].sudo().search([('customer_type', '=', 'stryker')])
        mail_list = []
        for members in teams.member_ids:
            if members.has_group('ppts_service_request.service_request_group_ct_user'):
                mail_list.append(members.login)
        mails = ', '.join(mail_list)
        template_id = request.env.ref('ppts_service_request.email_template_thermofisher_request')
        if ticket_type == 'thermofisher_fsm':
            action_id = request.env.ref('ppts_service_request.action_service_request_sr_fsm')
        else:
            action_id = request.env.ref('ppts_service_request.action_service_request')
        base_url = '/web#id=%d&action=%r&model=service.request&view_type=form' % (thermofisher_records.id, action_id.id)

        if template_id:
            template_id.with_context(email_to=mails, rec_url=base_url).sudo().send_mail(thermofisher_records.id,
                                                                                        force_send=True)
        values = {'thermofisher_records': thermofisher_records}
        if 'attachment' in request.params:
            attachment_list = request.httprequest.files.getlist('attachment')
            for image in attachment_list:
                if kw.get('attachment'):
                    attachments = {
                        'res_name': image.filename,
                        'res_model': 'service.request',
                        'res_id': thermofisher_records.id,
                        'datas': base64.encodestring(image.read()),
                        'type': 'binary',
                        # 'datas_fname': image.filename,
                        'name': image.filename,
                    }
                    attachment_obj = http.request.env['ir.attachment']
                    attachments_vals = attachment_obj.sudo().create(attachments)
                    thermofisher_records.update({
                        'attachment_ids': [(4, attachments_vals.id)],
                    })

        return request.render("ppts_service_request.thermofisher_request_thanks", values)

    @http.route(['/create/thermofisherrequest/installation'], type='http', auth="public", methods=['POST'],
                website=True)
    def create_thermofisher_request_installation(self, **kw):
        ticket_type = kw.get('ticket_type')
        if ticket_type == 'thermofisher_installation':
            installation_id = request.env['request.type'].sudo().search([('ticket_type', '=', 'sr_installation')],
                                                                        limit=1)
            team_id = request.env['crm.team'].sudo().search([('customer_type', '=', 'termo_fisher')], limit=1)
            thermofisher_request_vals = {
                'request_type_id': installation_id.id,
                'team_id': team_id.id,
                'requested_by_name': kw.get('customer_name'),
                'customer_name': kw.get('requested_by_name'),
                'requested_by_contact_number': kw.get('requested_by_contact_number'),
                'customer_email': kw.get('customer_email'),
                'customer_region_id': kw.get('customer_region_id'),
                'customer_street': kw.get('customer_street'),
                'customer_street2': kw.get('customer_street2'),
                'customer_city_id': kw.get('customer_city_id'),
                'customer_state_id': kw.get('customer_state_id'),
                'customer_zip': kw.get('customer_zip'),
                'customer_country_id': kw.get('customer_country_id'),
                'install_addr_street': kw.get('installation_location'),
                'location_contact_person': kw.get('location_contact_person'),
                'installation_date': kw.get('installation_date') or False,
                'service_category_id': kw.get('service_category_id'),
                'customer_po_number': kw.get('customer_po_no'),
                'customer_po_date': kw.get('customer_po_date') or False,
                'extended_invoice_number': kw.get('extended_warranty_invoice_no'),
                'extended_invoice_date': kw.get('extended_warranty_invoice_date') or False,
                'is_website_order': True,
                'product_part_code': kw.get('product_part_code'),
                'service_request_date': date.today(),
            }

        thermofisher_records = request.env['service.request'].sudo().create(thermofisher_request_vals)
        if request.env.user.has_group('ppts_service_request.service_request_group_user'):
            thermofisher_records.action_submit()
        teams = request.env['crm.team'].sudo().search([('customer_type', '=', 'stryker')])
        mail_list = []
        for members in teams.member_ids:
            if members.has_group('ppts_service_request.service_request_group_ct_user'):
                mail_list.append(members.login)
        mails = ', '.join(mail_list)
        template_id = request.env.ref('ppts_service_request.email_template_thermofisher_request')
        if ticket_type == 'thermofisher_installation':
            action_id = request.env.ref('ppts_service_request.action_service_request_sr_installation')
        else:
            action_id = request.env.ref('ppts_service_request.action_service_request')
        base_url = '/web#id=%d&action=%r&model=service.request&view_type=form' % (thermofisher_records.id, action_id.id)

        if template_id:
            template_id.with_context(email_to=mails, rec_url=base_url).sudo().send_mail(thermofisher_records.id,
                                                                                        force_send=True)
        values = {'thermofisher_records': thermofisher_records}
        if 'attachment' in request.params:
            attachment_list = request.httprequest.files.getlist('attachment')
            for image in attachment_list:
                if kw.get('attachment'):
                    attachments = {
                        'res_name': image.filename,
                        'res_model': 'service.request',
                        'res_id': thermofisher_records.id,
                        'datas': base64.encodestring(image.read()),
                        'type': 'binary',
                        # 'datas_fname': image.filename,
                        'name': image.filename,
                    }
                    attachment_obj = http.request.env['ir.attachment']
                    attachments_vals = attachment_obj.sudo().create(attachments)
                    thermofisher_records.update({
                        'attachment_ids': [(4, attachments_vals.id)],
                    })

        return request.render("ppts_service_request.thermofisher_request_thanks", values)
