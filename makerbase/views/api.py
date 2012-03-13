import json
import traceback

from flask import abort, request, Response
from flask.views import MethodView
from flaskext.login import login_required
from werkzeug.datastructures import MultiDict

from makerbase import app
from makerbase.forms import ProjectForm, ParticipationForm
from makerbase.models import *


class RobjectView(MethodView):

    def dispatch_request(self, *args, **kwargs):
        try:
            return super(RobjectView, self).dispatch_request(*args, **kwargs)
        except Exception, exc:
            return Response(json.dumps({
                "errors": [traceback.format_exc().split('\n')],
            }), 500)

    def render(self, obj):
        return json.dumps(obj.get_entity_data())


class ProjectAPI(RobjectView):

    def get(self, slug):
        # TODO: support a None slug for getting the project collection?
        proj = Project.get(slug)
        if proj is None:
            abort(404)

        return self.render(proj)

    @login_required
    def post(self, slug):
        proj = Project.get(slug)
        if proj is None:
            abort(404)

        proj_data = json.loads(request.data)

        form = ProjectForm(MultiDict(proj_data), proj)
        if not form.validate():
            return Response(json.dumps({
                "errors": form.errors,
            }), 400)

        # TODO: save a historical project item
        form.populate_obj(proj)
        proj.save()

        for party_data in proj_data['parties']:
            party_id = party_data.get('_id')
            if party_id is None:
                maker_id = party_data.get('maker_id')
                if maker_id is None:
                    continue
                maker = Maker.get(maker_id)
                party = Participation()

                party.add_link(maker, tag='maker')
                party.add_link(project, tag='project')
                maker.add_link(party, tag='participation')
                proj.add_link(party, tag='participation')
            else:
                party = Participation.get(party_id)

            form = ParticipationForm(MultiDict(party_data), party)
            if not form.validate():
                return Response(json.dumps({
                    'errors': form.errors,
                }), 400)

            form.populate_obj(party)
            party.save()

        return self.render(proj)


app.add_url_rule('/api/project/<slug>', view_func=ProjectAPI.as_view('api_project'))
