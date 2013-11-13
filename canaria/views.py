from pyramid.response import Response
from pyramid.view import view_config, view_defaults

import sqlalchemy.sql.functions as sqlfunc
from sqlalchemy.exc import DBAPIError
from .models import (
    DBSession,
    Activity,
    Mine,
    )


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'one': None}

class ViewObject(object):
    def __init__(self, request):
        self.request = request

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

        if not self.request.params.has_key('group'):
            activity = DBSession.query(Activity).filter(*criterion)
        else:
            values = []
            names = []
            group = []
            if self.request.params['group'] == 'state':
                values.append(Activity.state)
                group.append(Activity.state)
                names.append("state")
            else:
                values.append(Activity.state)
                values.append(Activity.county)
                group.append(Activity.state)
                group.append(Activity.county)
                names.append("state")
                names.append("county")
            values.append(sqlfunc.sum(Activity.production))
            names.append("production")
            values.append(sqlfunc.sum(Activity.average_employees))
            names.append("average_employees")
            values.append(sqlfunc.sum(Activity.labor_hours))
            names.append("labor_hours")

            results = DBSession.query(*values).filter(*criterion).group_by(*group).all()
            activity = []
            for row in results:
                d = {}
                for name, value in zip(names, row):
                    d[name] = value
                activity.append(d)
        
        return {'production': activity}

    @view_config(route_name='coalproduction_by_geo')
    def by_geo(self):
        return {}

    @view_config(route_name='coalproduction_by_mine')
    def by_mine(self):
        return {}

    def get_production(self, request, criterion):
        return 

