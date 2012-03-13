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

    def get(self, slug):
        obj = self.objclass.get(slug)
        if obj is None:
            abort(404)
        return self.render(obj)

    @login_required
    def post(self, slug):
        obj = self.objclass.get(slug)
        if obj is None:
            abort(404)

        data = json.loads(request.data)
        form = self.formclass(MultiDict(data), obj)
        if not form.validate():
            return Response(json.dumps({
                'errors': form.errors,
            }), 400)

        form.populate_obj(obj)
        obj.save()

        return self.render(obj)


class ProjectAPI(RobjectView):

    objclass = Project
    formclass = ProjectForm


app.add_url_rule('/api/project/<slug>', view_func=ProjectAPI.as_view('api_project'))


class ParticipationAPI(RobjectView):

    objclass = Participation
    formclass = ParticipationForm


app.add_url_rule('/api/participation/<slug>', view_func=ParticipationAPI.as_view('api_participation'))
