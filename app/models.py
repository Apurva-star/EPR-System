from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }


class SKU(db.Model):
  
    __tablename__ = "skus"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sku_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    product_name = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    cat_i_rigid = db.Column(
        db.Float,
        default=0.0
    )

    cat_ii_flexible = db.Column(
        db.Float,
        default=0.0
    )

    cat_iii_mlp = db.Column(
        db.Float,
        default=0.0
    )

    cat_iv_bio = db.Column(
        db.Float,
        default=0.0
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sku_code": self.sku_code,
            "product_name": self.product_name,
            "cat_i_rigid": self.cat_i_rigid,
            "cat_ii_flexible": self.cat_ii_flexible,
            "cat_iii_mlp": self.cat_iii_mlp,
            "cat_iv_bio": self.cat_iv_bio,
        }


ProductMaster = SKU

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    category_name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )
# sale cvs file data 
class Credit(db.Model):
    __tablename__ = "credits"

    id = db.Column(db.Integer, primary_key=True)

    pwp_name = db.Column(
        db.String(100),
        nullable=False
    )

    pwp_cpcb_reg_no = db.Column(
        db.String(50),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    category = db.relationship(
        "Category",
        backref="credits"
    )

    tonnage_mt = db.Column(
        db.Float,
        nullable=False
    )

    purchase_date = db.Column(
        db.String(20)
    )

    purchase_cost = db.Column(
        db.Float
    )

    cpcb_ref_no = db.Column(
        db.String(100),
        unique=True
    )

    gst_invoice_no = db.Column(
        db.String(50)
    )


class SalesLog(db.Model):
    __tablename__ = "sales_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    financial_year = db.Column(
        db.String(20),
        nullable=False
    )

    reporting_month = db.Column(
        db.String(20),
        nullable=False
    )

    # Store internal SKU ID
    sku_id = db.Column(
        db.Integer,
        db.ForeignKey("skus.id"),
        nullable=False
    )

    sku = db.relationship(
        "SKU",
        backref="sales_logs"
    )

    units_sold = db.Column(
        db.Integer,
        nullable=False
    )

    category_i_mt = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    category_ii_mt = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    category_iii_mt = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    category_iv_mt = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    calculated_plastic_mt = db.Column(
        db.Float,
        nullable=False,
        default=0
    )

    def to_dict(self):
        return {
            "id": self.id,
            "financial_year": self.financial_year,
            "reporting_month": self.reporting_month,

            "sku_id": self.sku_id,

            # This shows SKU code in API response
            "sku_code": self.sku.sku_code
                if self.sku else None,

            "product_name": self.sku.product_name
                if self.sku else None,

            "units_sold": self.units_sold,

            "category_i_mt": self.category_i_mt,
            "category_ii_mt": self.category_ii_mt,
            "category_iii_mt": self.category_iii_mt,
            "category_iv_mt": self.category_iv_mt,
            "calculated_plastic_mt":
                self.calculated_plastic_mt
        }