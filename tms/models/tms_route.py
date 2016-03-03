# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################


from openerp.osv import osv, fields
from openerp.tools.translate import _
import simplejson as json
import urllib as my_urllib


# Routes
class tms_route(osv.osv):
    _name ='tms.route'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Routes'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=False),
        'name' : fields.char('Route Name', size=64, required=True, select=True),
        'departure_id': fields.many2one('tms.place', 'Departure', required=True),
        'arrival_id': fields.many2one('tms.place', 'Arrival', required=True),
        'distance':fields.float('Distance (mi./kms)', required=True, digits=(14,4), help='Route distance (mi./kms)'),
        'places_ids' : fields.one2many('tms.route.place', 'route_id', 'Intermediate places in Route'),
        'travel_time':fields.float('Travel Time (hrs)', required=True, digits=(14,4), help='Route travel time (hours)'),
        'route_fuelefficiency_ids' : fields.one2many('tms.route.fuelefficiency', 'tms_route_id', 'Fuel Efficiency by Motor type'),
        'fuel_efficiency_drive_unit': fields.float('Fuel Efficiency Drive Unit', required=False, digits=(14,4)),
        'fuel_efficiency_1trailer': fields.float('Fuel Efficiency One Trailer', required=False, digits=(14,4)),
        'fuel_efficiency_2trailer': fields.float('Fuel Efficiency Two Trailer', required=False, digits=(14,4)),
        'notes': fields.text('Notes'),
        'active':fields.boolean('Active'),
        'tms_route_tollstation_ids' : fields.many2many('tms.route.tollstation', 'tms_route_tollstation_route_rel', 'tollstation_id', 'route_id', 'Toll Station in this Route'),
        }

    _defaults = {
        'active': True,
    }

    def _check_distance(self, cr, uid, ids, context=None):
        return (self.browse(cr, uid, ids, context=context)[0].distance > 0)

    _constraints = [
        (_check_distance, 'You can not save New Route without Distance!', ['distance']),
        ]

    def  button_get_route_info(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            if rec.departure_id.latitude and rec.departure_id.longitude and rec.arrival_id.latitude and rec.arrival_id.longitude:
                destinations = ""
                origins = str(rec.departure_id.latitude) + ',' + str(rec.departure_id.longitude)
                places = [str(x.place_id.latitude) + ',' + str(x.place_id.longitude) for x in rec.places_ids if x.place_id.latitude and x.place_id.longitude]                        
                #print "places: ", places
                for place in places:
                    origins += "|" + place
                    destinations += place + "|"
                destinations += str(rec.arrival_id.latitude) +',' + str(rec.arrival_id.longitude)
                #print "origins: ", origins
                #print "destinations: ", destinations
                google_url = 'http://maps.googleapis.com/maps/api/distancematrix/json?origins=' + origins + \
                                                                                '&destinations=' + destinations + \
                                                                                '&mode=driving' + \
                                                                                '&language=' + context['lang'][:2] + \
                                                                                '&sensor=false'
                result = json.load(my_urllib.urlopen(google_url))
                if result['status'] == 'OK':
                    distance = duration = 0.0
                    if len(rec.places_ids):
                        i = 0
                        for row in result['rows']:
                            #print row
                            distance += row['elements'][i]['distance']['value'] / 1000.0
                            duration += row['elements'][i]['duration']['value'] / 3600.0
                            i += 1
                    else:
                        distance = result['rows'][0]['elements'][0]['distance']['value'] / 1000.0
                        duration = result['rows'][0]['elements'][0]['duration']['value'] / 3600.0

                    #print "distance: ", distance
                    #print "duration: ", duration

                    self.write(cr, uid, ids, {'distance': distance, 'travel_time' : duration })
                #else:
                    #print result['status']
            else:
                raise osv.except_osv(_('Error !'), _('You cannot get route info because one of the places has no coordinates.'))

        return True

    def button_open_google(self, cr, uid, ids, context=None):
        for route in self.browse(cr, uid, ids):
            points = str(route.departure_id.latitude) + ','+ str(route.departure_id.longitude) + (',' if len(route.places_ids) else '') +  \
                        ','.join([str(x.place_id.latitude) + ',' + str(x.place_id.longitude) for x in route.places_ids if x.place_id.latitude and x.place_id.longitude]) + \
                        ',' + str(route.arrival_id.latitude) + ','+ str(route.arrival_id.longitude)
            #print points
            url="/tms/static/src/googlemaps/get_route.html?" + points
        return { 'type': 'ir.actions.act_url', 'url': url, 'nodestroy': True, 'target': 'new' }