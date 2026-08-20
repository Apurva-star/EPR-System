from flask import Blueprint, request, jsonify
from app import db
from app.models import SKU

tasks_bp = Blueprint("tasks", __name__)


# GET - Read all SKUs
@tasks_bp.route("/api/skus", methods=["GET"])
def get_skus():

    skus = SKU.query.all()

    return jsonify(
        [sku.to_dict() for sku in skus]
    ), 200


# POST - Create SKU
@tasks_bp.route("/api/skus", methods=["POST"])
def create_sku():

    data = request.get_json()

    if not data or "sku_code" not in data or "product_name" not in data:
        return jsonify({
            "error": "Missing mandatory fields (sku_code, product_name)"
        }), 400

    # Check duplicate SKU
    existing_sku = db.session.get(
        SKU,
        data["sku_code"]
    )

    if existing_sku:
        return jsonify({
            "error": "SKU Code already exists"
        }), 400

    new_sku = SKU(
        sku_code=data["sku_code"],
        product_name=data["product_name"],
        cat_i_rigid=float(
            data.get("cat_i_rigid", 0.0)
        ),
        cat_ii_flexible=float(
            data.get("cat_ii_flexible", 0.0)
        ),
        cat_iii_mlp=float(
            data.get("cat_iii_mlp", 0.0)
        ),
        cat_iv_bio=float(
            data.get("cat_iv_bio", 0.0)
        )
    )

    db.session.add(new_sku)
    db.session.commit()

    return jsonify({
        "message": "SKU profile created successfully",
        "sku": new_sku.to_dict()
    }), 201


# PUT - Update SKU
@tasks_bp.route("/api/skus/<string:sku_code>", methods=["PUT"])
def update_sku(sku_code):

    sku = db.session.get(
        SKU,
        sku_code
    )

    if not sku:
        return jsonify({
            "error": "SKU not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data provided"
        }), 400

    sku.product_name = data.get(
        "product_name",
        sku.product_name
    )

    sku.cat_i_rigid = float(
        data.get(
            "cat_i_rigid",
            sku.cat_i_rigid
        )
    )

    sku.cat_ii_flexible = float(
        data.get(
            "cat_ii_flexible",
            sku.cat_ii_flexible
        )
    )

    sku.cat_iii_mlp = float(
        data.get(
            "cat_iii_mlp",
            sku.cat_iii_mlp
        )
    )

    sku.cat_iv_bio = float(
        data.get(
            "cat_iv_bio",
            sku.cat_iv_bio
        )
    )

    db.session.commit()

    return jsonify({
        "message": "SKU updated successfully",
        "sku": sku.to_dict()
    }), 200


# DELETE - Delete SKU
@tasks_bp.route(
    "/api/skus/<string:sku_code>",
    methods=["DELETE"]
)
def delete_sku(sku_code):

    sku = db.session.get(
        SKU,
        sku_code
    )

    if not sku:
        return jsonify({
            "error": "SKU not found"
        }), 404

    db.session.delete(sku)
    db.session.commit()

    return jsonify({
        "message": "SKU deleted successfully"
    }), 200
