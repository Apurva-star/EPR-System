import csv
import io

from flask import Blueprint, jsonify, request

from app import db
from app.models import SKU, SalesLog


# Create Sales Blueprint
sales_bp = Blueprint("sales", __name__)


@sales_bp.route("/api/sales/upload", methods=["POST"])
def upload_sales():

    # -----------------------------------
    # 1. Get form fields
    # -----------------------------------

    financial_year = request.form.get("financial_year")
    reporting_month = request.form.get("reporting_month")

    if not financial_year or not reporting_month:
        return jsonify({
            "error": "Financial year and reporting month are required"
        }), 400


    # -----------------------------------
    # 2. Check CSV file
    # -----------------------------------

    if "file" not in request.files:
        return jsonify({
            "error": "No file uploaded"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "Selected file has no filename"
        }), 400


    try:

        # -----------------------------------
        # 3. Read CSV
        # -----------------------------------

        stream = io.TextIOWrapper(
            file.stream,
            encoding="utf-8"
        )

        csv_reader = csv.DictReader(stream)


        # -----------------------------------
        # 4. Initialize totals
        # -----------------------------------

        valid_rows = 0

        total_category_i_grams = 0
        total_category_ii_grams = 0
        total_category_iii_grams = 0
        total_category_iv_grams = 0

        logs_to_save = []


        # -----------------------------------
        # 5. Process each CSV row
        # -----------------------------------

        for row in csv_reader:

            sku_code = row["sku_code"].strip()

            units_sold = int(row["units_sold"])


            # -----------------------------------
            # 6. Find SKU in database
            # -----------------------------------

            sku_item = SKU.query.get(sku_code)

            if not sku_item:
                # SKU doesn't exist in master
                # Skip this row
                continue


            # -----------------------------------
            # 7. Category-wise plastic
            #    weight in grams
            # -----------------------------------

            category_i_grams = (
                units_sold * sku_item.cat_i_rigid
            )

            category_ii_grams = (
                units_sold * sku_item.cat_ii_flexible
            )

            category_iii_grams = (
                units_sold * sku_item.cat_iii_mlp
            )

            category_iv_grams = (
                units_sold * sku_item.cat_iv_bio
            )


            # -----------------------------------
            # 8. Convert grams → Metric Tonnes
            # -----------------------------------

            category_i_mt = (
                category_i_grams / 1_000_000.0
            )

            category_ii_mt = (
                category_ii_grams / 1_000_000.0
            )

            category_iii_mt = (
                category_iii_grams / 1_000_000.0
            )

            category_iv_mt = (
                category_iv_grams / 1_000_000.0
            )


            # -----------------------------------
            # 9. Total plastic for this SKU
            # -----------------------------------

            total_plastic_mt = (
                category_i_mt
                + category_ii_mt
                + category_iii_mt
                + category_iv_mt
            )


            # -----------------------------------
            # 10. Add to batch totals
            # -----------------------------------

            total_category_i_grams += category_i_grams
            total_category_ii_grams += category_ii_grams
            total_category_iii_grams += category_iii_grams
            total_category_iv_grams += category_iv_grams


            # -----------------------------------
            # 11. Create SalesLog
            # -----------------------------------

            new_log = SalesLog(

                financial_year=financial_year,

                reporting_month=reporting_month,

                sku_code=sku_code,

                units_sold=units_sold,

                category_i_mt=category_i_mt,

                category_ii_mt=category_ii_mt,

                category_iii_mt=category_iii_mt,

                category_iv_mt=category_iv_mt,

                calculated_plastic_mt=total_plastic_mt
            )


            logs_to_save.append(new_log)

            valid_rows += 1


        # -----------------------------------
        # 12. Save all records
        # -----------------------------------

        db.session.bulk_save_objects(logs_to_save)

        db.session.commit()


        # -----------------------------------
        # 13. Calculate batch totals
        # -----------------------------------

        batch_category_i_mt = (
            total_category_i_grams / 1_000_000.0
        )

        batch_category_ii_mt = (
            total_category_ii_grams / 1_000_000.0
        )

        batch_category_iii_mt = (
            total_category_iii_grams / 1_000_000.0
        )

        batch_category_iv_mt = (
            total_category_iv_grams / 1_000_000.0
        )


        # -----------------------------------
        # 14. Total plastic for entire CSV
        # -----------------------------------

        batch_total_mt = (
            batch_category_i_mt
            + batch_category_ii_mt
            + batch_category_iii_mt
            + batch_category_iv_mt
        )


        # -----------------------------------
        # 15. Return response
        # -----------------------------------

        return jsonify({

            "message":
                "Sales file processed successfully",

            "valid_records_identified":
                valid_rows,

            "category_i_mt":
                round(batch_category_i_mt, 4),

            "category_ii_mt":
                round(batch_category_ii_mt, 4),

            "category_iii_mt":
                round(batch_category_iii_mt, 4),

            "category_iv_mt":
                round(batch_category_iv_mt, 4),

            "total_plastic_mt":
                round(batch_total_mt, 4)

        }), 201


    except Exception as e:

        # Rollback if something goes wrong
        db.session.rollback()

        return jsonify({
            "error": str(e)
        }), 500