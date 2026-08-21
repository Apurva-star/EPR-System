from flask import Blueprint, request, jsonify
from app import db
from app.models import SKU, Credit, Category


tasks_bp = Blueprint("tasks", __name__)


# =========================================================
# SKU APIs
# =========================================================


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


# =========================================================
# CREDIT API
# =========================================================


# POST - Create Credit
@tasks_bp.route("/api/credits", methods=["POST"])
def add_credit():

    data = request.get_json()

    # -----------------------------------
    # 1. Check JSON
    # -----------------------------------

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400


    # -----------------------------------
    # 2. Required fields
    # -----------------------------------

    required_fields = [
        "pwp_name",
        "pwp_cpcb_reg_no",
        "category",
        "tonnage_mt",
        "purchase_date",
        "purchase_cost",
        "cpcb_ref_no",
        "gst_invoice_no"
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing fields",
            "fields": missing_fields
        }), 400


    existing_credit = Credit.query.filter_by(
        cpcb_ref_no=data["cpcb_ref_no"]
    ).first()

    if existing_credit:
        return jsonify({
            "error": "CPCB reference number already exists",
            "cpcb_ref_no": data["cpcb_ref_no"]
        }), 400


    # -----------------------------------
    # 3. Find category from Category Master
    # -----------------------------------

    category = Category.query.filter_by(
        category_name=data["category"]
    ).first()

    if not category:
        return jsonify({
            "error": "Invalid category",
            "message": (
                "Category must be Rigid, Flexible, "
                "MLP or Bio"
            )
        }), 400


    # -----------------------------------
    # 4. Create Credit
    # -----------------------------------

    new_credit = Credit(

        pwp_name=data["pwp_name"],

        pwp_cpcb_reg_no=data["pwp_cpcb_reg_no"],

        # IMPORTANT:
        # Store only Category ID in database
        category_id=category.id,

        tonnage_mt=float(
            data["tonnage_mt"]
        ),

        purchase_date=data["purchase_date"],

        purchase_cost=float(
            data["purchase_cost"]
        ),

        cpcb_ref_no=data["cpcb_ref_no"],

        gst_invoice_no=data["gst_invoice_no"]
    )


    # -----------------------------------
    # 5. Save Credit
    # -----------------------------------

    db.session.add(new_credit)
    db.session.commit()


    # -----------------------------------
    # 6. Response
    # -----------------------------------

    return jsonify({

        "message": "Credit created successfully",

        "credit": {

            "id": new_credit.id,

            "pwp_name": new_credit.pwp_name,

            "pwp_cpcb_reg_no":
                new_credit.pwp_cpcb_reg_no,

            # Display category NAME
            "category":
                category.category_name,

            "tonnage_mt":
                new_credit.tonnage_mt,

            "purchase_date":
                new_credit.purchase_date,

            "purchase_cost":
                new_credit.purchase_cost,

            "cpcb_ref_no":
                new_credit.cpcb_ref_no,

            "gst_invoice_no":
                new_credit.gst_invoice_no
        }

    }), 201