
from flask import Blueprint, jsonify
from sqlalchemy.sql import func

from app import db
from app.models import SalesLog, Credit


reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/api/reports/form-1", methods=["GET"])
def get_form1_report():

    # -------------------------------------------------
    # 1. Get actual category-wise plastic totals
    #    from SalesLog table
    # -------------------------------------------------

    category_i_sold = (
        db.session.query(
            func.sum(SalesLog.category_i_mt)
        ).scalar()
        or 0.0
    )

    category_ii_sold = (
        db.session.query(
            func.sum(SalesLog.category_ii_mt)
        ).scalar()
        or 0.0
    )

    category_iii_sold = (
        db.session.query(
            func.sum(SalesLog.category_iii_mt)
        ).scalar()
        or 0.0
    )

    category_iv_sold = (
        db.session.query(
            func.sum(SalesLog.category_iv_mt)
        ).scalar()
        or 0.0
    )


    # -------------------------------------------------
    # 2. Target percentage
    # -------------------------------------------------

    target_percentage = 0.70


    # -------------------------------------------------
    # 3. Get certificates / credits from database
    #
    # NOTE:
    # This currently gets TOTAL Credit tonnage.
    # For category-wise offset, Credit table should
    # contain category information.
    # -------------------------------------------------

    total_certificates_procured = (
        db.session.query(
            func.sum(Credit.tonnage_mt)
        ).scalar()
        or 0.0
    )


    # -------------------------------------------------
    # 4. Calculate category-wise target
    # -------------------------------------------------

    cat_i_target = category_i_sold * target_percentage
    cat_ii_target = category_ii_sold * target_percentage
    cat_iii_target = category_iii_sold * target_percentage
    cat_iv_target = category_iv_sold * target_percentage


    # -------------------------------------------------
    # 5. For now, calculate total target
    # -------------------------------------------------

    total_mandated = (
        cat_i_target
        + cat_ii_target
        + cat_iii_target
        + cat_iv_target
    )


    # -------------------------------------------------
    # 6. Total deficit
    # -------------------------------------------------

    total_deficit = max(
        0.0,
        total_mandated - total_certificates_procured
    )


    # -------------------------------------------------
    # 7. Compliance percentage
    # -------------------------------------------------

    overall_compliance = (
        min(
            100.0,
            (
                total_certificates_procured
                / total_mandated
                * 100
            )
        )
        if total_mandated > 0
        else 100.0
    )


    # -------------------------------------------------
    # 8. Fine risk
    # -------------------------------------------------

    fine_rate_per_mt = 3000.0

    fine_risk = (
        total_deficit * fine_rate_per_mt
    )


    # -------------------------------------------------
    # 9. Create Form-1 category rows
    # -------------------------------------------------

    report_rows = [

        {
            "category": "Cat I (Rigid)",
            "total_sold_mt": round(
                category_i_sold, 2
            ),
            "target_percentage": 70,
            "mandated_mt": round(
                cat_i_target, 2
            )
        },

        {
            "category": "Cat II (Flexible)",
            "total_sold_mt": round(
                category_ii_sold, 2
            ),
            "target_percentage": 70,
            "mandated_mt": round(
                cat_ii_target, 2
            )
        },

        {
            "category": "Cat III (MLP)",
            "total_sold_mt": round(
                category_iii_sold, 2
            ),
            "target_percentage": 70,
            "mandated_mt": round(
                cat_iii_target, 2
            )
        },

        {
            "category": "Cat IV (Bio)",
            "total_sold_mt": round(
                category_iv_sold, 2
            ),
            "target_percentage": 70,
            "mandated_mt": round(
                cat_iv_target, 2
            )
        }

    ]


    # -------------------------------------------------
    # 10. Return Form-1
    # -------------------------------------------------

    return jsonify({

        "entity_name":
            "Ishwarya FMCG Goods Private Limited",

        "cpcb_reg_no":
            "PIBO-MH-2024-001",

        "assessment_year":
            "2025-2026",

        "filing_status":
            (
                "Deficit Pending"
                if total_deficit > 0
                else "Fully Compliant"
            ),

        "reconciliation_matrix":
            report_rows,

        "summary": {

            "total_sold_mt":
                round(
                    category_i_sold
                    + category_ii_sold
                    + category_iii_sold
                    + category_iv_sold,
                    2
                ),

            "total_mandated_mt":
                round(total_mandated, 2),

            "total_certificates_procured_mt":
                round(
                    total_certificates_procured,
                    2
                ),

            "total_deficit_mt":
                round(total_deficit, 2),

            "overall_compliance_percent":
                round(overall_compliance, 2),

            "estimated_fine_liability_inr":
                round(fine_risk, 2)
        }

    }), 200