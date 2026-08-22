

from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.sql import func

from flask import Blueprint, request, jsonify
from app import db
from app.models import SKU, Credit, Category, SalesLog


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


@tasks_bp.route("/api/products", methods=["GET"])
def get_products():

    products = SKU.query.order_by(SKU.product_name).all()

    return jsonify(
        [product.to_dict() for product in products]
    ), 200


# POST - Create SKU

@tasks_bp.route("/api/skus", methods=["POST"])
def create_sku():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    # Required fields
    required_fields = [
        "sku_code",
        "product_name"
    ]

    missing_fields = [
        field
        for field in required_fields
        if not data.get(field)
    ]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing_fields
        }), 400


    # Check product name
    existing_product = SKU.query.filter_by(
        product_name=data["product_name"]
    ).first()

    if existing_product:
        existing_product.cat_i_rigid = float(
            data.get("cat_i_rigid", existing_product.cat_i_rigid)
        )
        existing_product.cat_ii_flexible = float(
            data.get("cat_ii_flexible", existing_product.cat_ii_flexible)
        )
        existing_product.cat_iii_mlp = float(
            data.get("cat_iii_mlp", existing_product.cat_iii_mlp)
        )
        existing_product.cat_iv_bio = float(
            data.get("cat_iv_bio", existing_product.cat_iv_bio)
        )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "error": "Product update conflicts with existing data"
            }), 400
        except OperationalError:
            db.session.rollback()
            return jsonify({
                "error": "Database is busy. Close the SQLite database viewer and try again."
            }), 503

        return jsonify({
            "message": "Product weights updated successfully",
            "sku": existing_product.to_dict()
        }), 200


    # Check SKU code for new products
    existing_sku = SKU.query.filter_by(
        sku_code=data["sku_code"]
    ).first()

    if existing_sku:
        return jsonify({
            "error": "SKU code already exists"
        }), 400


    # Create SKU
    new_sku = SKU(

        sku_code=data["sku_code"],

        product_name=data["product_name"],

        cat_i_rigid=float(
            data.get("cat_i_rigid", 0)
        ),

        cat_ii_flexible=float(
            data.get("cat_ii_flexible", 0)
        ),

        cat_iii_mlp=float(
            data.get("cat_iii_mlp", 0)
        ),

        cat_iv_bio=float(
            data.get("cat_iv_bio", 0)
        )
    )


    db.session.add(new_sku)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "SKU code or product name already exists"
        }), 400
    except OperationalError:
        db.session.rollback()
        return jsonify({
            "error": "Database is busy. Close the SQLite database viewer and try again."
        }), 503


    return jsonify({

        "message": "SKU created successfully",

        "sku": new_sku.to_dict()

    }), 201

# PUT - Update SKU using sku_code from JSON
@tasks_bp.route("/api/skus", methods=["PUT"])
def update_sku_from_json():

    data = request.get_json()

    if not data or not data.get("sku_code"):
        return jsonify({
            "error": "sku_code is required for update"
        }), 400

    return update_sku(data["sku_code"])


# PUT - Update SKU using sku_code in the URL
@tasks_bp.route("/api/skus/<string:sku_code>", methods=["PUT"])
def update_sku(sku_code):

    sku = SKU.query.filter_by(
    sku_code=sku_code
  ).first()

    if not sku and sku_code.isdigit():
        sku = db.session.get(SKU, int(sku_code))

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

    sku = SKU.query.filter_by(
    sku_code=sku_code
  ).first()
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


# DELETE - Delete Credit
@tasks_bp.route("/api/credits/<int:credit_id>", methods=["DELETE"])
def delete_credit(credit_id):

    credit = Credit.query.get(credit_id)

    if not credit:
        return jsonify({
            "error": "Credit not found"
        }), 404

    db.session.delete(credit)
    db.session.commit()

    return jsonify({
        "message": "Credit deleted successfully",
        "credit_id": credit_id
    }), 200


# =========================================================
# DASHBOARD SUMMARY API
# =========================================================

@tasks_bp.route("/api/dashboard", methods=["GET"])
@tasks_bp.route("/api/dashboard/summary", methods=["GET"])
def get_dashboard_summary():

    # -----------------------------------------------------
    # 1. Total plastic calculated from SalesLog
    # -----------------------------------------------------

    total_plastic_sold = (
        db.session.query(
            func.sum(SalesLog.calculated_plastic_mt)
        ).scalar()
        or 0.0
    )


    # -----------------------------------------------------
    # 2. EPR Target
    # Example: 70% of total plastic
    # -----------------------------------------------------

    target_percentage = 0.70

    mandated_target = (
        total_plastic_sold * target_percentage
    )


    # -----------------------------------------------------
    # 3. Total EPR Credits Purchased
    # This comes from Credit table
    # -----------------------------------------------------

    purchased_credits = (
        db.session.query(
            func.sum(Credit.tonnage_mt)
        ).scalar()
        or 0.0
    )


    # -----------------------------------------------------
    # 4. Remaining / Deficit
    # -----------------------------------------------------

    deficit = max(
        0.0,
        mandated_target - purchased_credits
    )


    # -----------------------------------------------------
    # 5. Fine Risk
    # -----------------------------------------------------

    fine_rate_per_mt = 3000.0

    fine_risk = (
        deficit * fine_rate_per_mt
    )


    # -----------------------------------------------------
    # 6. Compliance Score
    # -----------------------------------------------------

    compliance_score = min(
        100.0,
        (purchased_credits / mandated_target * 100)
        if mandated_target > 0
        else 100.0
    )


    # -----------------------------------------------------
    # Return dashboard data
    # -----------------------------------------------------

    return jsonify({

        "total_plastic_mt":
            round(total_plastic_sold, 2),

        "mandated_target_mt":
            round(mandated_target, 2),

        "purchased_credits_mt":
            round(purchased_credits, 2),

        "compliance_score_percent":
            round(compliance_score, 1),

        "deficit_mt":
            round(deficit, 2),

        "fine_risk_inr":
            round(fine_risk, 2)

    }), 200