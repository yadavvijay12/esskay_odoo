# -*- coding: utf-8 -*-
#############################################################################
#
#    Point Perfect Technology Solutions.
#
#############################################################################
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError


class GeoLocation(models.Model):
    _name = 'geo.location'

    name = fields.Char(string="Name")
    latitude_longitude_ids = fields.One2many('lat.long', 'lat_long_id', string="Latitude&Longitude")
    user_id = fields.Many2one("res.users", string='Users')


class LatLong(models.Model):
    _name = 'lat.long'

    longitude = fields.Float(string="Longitude")
    latitude = fields.Float(string="Latitude")
    lat_long_id = fields.Many2one("geo.location", string='Lat & Long')
