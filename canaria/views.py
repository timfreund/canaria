from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

import sqlalchemy.sql.functions as sqlfunc
from sqlalchemy.exc import DBAPIError
from .models import (
    DBSession,
    Activity,
    Mine,
    )

class ViewObject(object):
    def __init__(self, request):
        self.request = request

class BrowserView(ViewObject):
    def __init__(self, request):
        ViewObject.__init__(self, request)
        renderer = get_renderer('templates/main_template.pt')
        self.main_template = renderer.implementation().macros['master']

        self.piwik_host = None
        if request.registry.settings.has_key('piwik.host'):
            self.piwik_host = request.registry.settings['piwik.host']
            self.piwik_id = request.registry.settings['piwik.site_id']

class AnonymousViews(BrowserView):
    @view_config(renderer='templates/api.pt', route_name='apidocs')
    def api(self):
        return {}

    @view_config(renderer='templates/home.pt', route_name='/')
    def home(self):
        return {}

class DemoViews(BrowserView):
    @view_config(renderer='templates/demo_map.pt', route_name='demo_map')
    def map(self):
        return {}

@view_defaults(renderer='json')
class CoalProductionViews(ViewObject):
    @view_config(route_name='coalproduction_by_us')
    def by_us_location(self):
        criterion = []
        location = self.request.matchdict['location']
        if len(location) == 2:
            criterion.append(Activity.county == location[1])
        if len(location) >= 1:
            criterion.append(Activity.state.like('%s%%' % location[0]))
        if self.request.matchdict['year'] != '*':
            # TODO - if year == '*', should we group by year?
            criterion.append(Activity.year == self.request.matchdict['year'])

        group_type = self.request.params.get('group', None)
        activity = self.get_production(criterion, group_type)

        return {'data': activity,}

    @view_config(route_name='coalproduction_by_geo')
    def by_geo(self):
        return {}

    @view_config(route_name='coalproduction_by_mine')
    def by_mine(self):
        criterion = []
        criterion.append(Activity.mine_id == self.request.matchdict['mine_id'])
        if self.request.matchdict['year'] != '*':
            # TODO - if year == '*', should we group by year?
            criterion.append(Activity.year == self.request.matchdict['year'])
        activity = self.get_production(criterion)
        return {'data': activity,}

    def get_production(self, criterion, group_type=None):
        activity = []

        if group_type:
            activity = self.get_grouped_production(criterion, group_type)
        else:
            for row in DBSession.query(Activity).filter(*criterion).all():
                activity.append(row)
        return activity

    def get_grouped_production(self, criterion, group_type):
        activity = []
        if group_type in ['state', 'county']:
            values = []
            names = []
            group = []

            values.append(Activity.state)
            group.append(Activity.state)
            names.append("state")

            if group_type == 'county':
                values.append(Activity.county)
                group.append(Activity.county)
                names.append("county")

            values.append(sqlfunc.sum(Activity.production))
            names.append("production")
            values.append(sqlfunc.sum(Activity.average_employees))
            names.append("average_employees")
            values.append(sqlfunc.sum(Activity.labor_hours))
            names.append("labor_hours")

            results = DBSession.query(*values).filter(*criterion).group_by(*group).all()
            for row in results:
                d = {}
                for name, value in zip(names, row):
                    d[name] = value
                activity.append(d)
        else:
            raise Exception("Invalid group type: %s" % group_type)

        return activity
