from flask.views import MethodView
from flask import request, jsonify, g
from marshmallow.exceptions import ValidationError

from .utils import error_response, auth_required, pagination
from .models import db


class DetailAPI(MethodView):
    init_every_request = False

    def __init__(self, model, schema):
        self.model = model
        self.schema = schema()

    def _get_obj(self, id):
        return db.session.get(self.model, id)

    def get(self, id):
        item = self._get_obj(id)
        if not item:
            return self.return_404()

        data = self.schema.dump(item)
        return jsonify(data)

    @auth_required
    def patch(self, id):
        obj = self._get_obj(id)
        if not obj:
            return self.return_404()

        if not obj.author_id == g.user.get('id'):
            return error_response("You can not update this item.")

        author_id = request.json.get("author_id")
        if author_id and not author_id == obj.author_id:
            return error_response("You can not change author.")

        try:
            data = self.schema.load(request.json, partial=True)
            obj.update(data)
            data = self.schema.dump(obj)
            return jsonify(data)
        except ValidationError as e:
            return error_response(e.messages)

    @auth_required
    def delete(self, id):
        obj = self._get_obj(id)
        if not obj:
            return self.return_404()

        if not obj.author_id == g.user.get('id'):
            return error_response("You can not delete this item.")

        obj.delete()
        return jsonify({'message': 'Deleted'}), 204

    def return_404(self):
        return error_response("Item does not exist", code=404)


class ListAPI(MethodView):
    init_every_request = False

    def __init__(self, model, schema):
        self.model = model
        self.schema = schema()

    def get(self):
        response = pagination(request, db.select(self.model), self.schema)
        return jsonify(response)

    @auth_required
    def post(self):
        req_data = request.get_json()
        req_data['author_id'] = g.user.get('id')
        try:
            data = self.schema.load(req_data)
            obj = self.model(**data)
            obj.save()
            data = self.schema.dump(obj)
            return jsonify(data), 201
        except ValidationError as e:
            return error_response(e.messages)


def register_api(app, model, schema, name):
    item = DetailAPI.as_view(f"{name}-detail", model, schema)
    group = ListAPI.as_view(f"{name}-list", model, schema)
    app.add_url_rule(f"/{name}/<int:id>", view_func=item)
    app.add_url_rule(f"/{name}/", view_func=group)
