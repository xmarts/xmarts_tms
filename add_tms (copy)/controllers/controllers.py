# -*- coding: utf-8 -*-
from odoo import http

# class AddTms(http.Controller):
#     @http.route('/add_tms/add_tms/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/add_tms/add_tms/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('add_tms.listing', {
#             'root': '/add_tms/add_tms',
#             'objects': http.request.env['add_tms.add_tms'].search([]),
#         })

#     @http.route('/add_tms/add_tms/objects/<model("add_tms.add_tms"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('add_tms.object', {
#             'object': obj
#         })