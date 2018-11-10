from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, fresh_jwt_required

from models.item import ItemModel
from schemas.item import ItemSchema
from lib.strings import gettext

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {"message": gettext("item_not_found")}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {"message": gettext("item_name_exists").format(name)}, 400

        item_dict = request.get_json()
        item_dict["name"] = name
        item = item_schema.load(item_dict)
        try:
            item.save_to_db()
        except Exception:
            return {"message": gettext("item_error_inserting")}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": gettext("item_deleted")}, 200
        return {"message": gettext("item_not_found")}, 404

    @classmethod
    def put(cls, name: str):
        item_dict = request.get_json()
        item = ItemModel.find_by_name(name)
        if item:
            item.price = item_dict["price"]
        else:
            item_dict["name"] = name
            item = item_schema.load(item_dict)
        item.save_to_db()
        return item_schema.dump(item), 200


class ItemList(Resource):
    @classmethod
    def get(cls):
        return {"items": item_list_schema.dump(ItemModel.find_all())}, 200
