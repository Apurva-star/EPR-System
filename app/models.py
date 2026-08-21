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

    sku_code = db.Column(db.String(50), primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    cat_i_rigid = db.Column(db.Float, default=0.0)
    cat_ii_flexible = db.Column(db.Float, default=0.0)
    cat_iii_mlp = db.Column(db.Float, default=0.0)
    cat_iv_bio = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            "sku_code": self.sku_code,
            "product_name": self.product_name,
            "cat_i_rigid": self.cat_i_rigid,
            "cat_ii_flexible": self.cat_ii_flexible,
            "cat_iii_mlp": self.cat_iii_mlp,
            "cat_iv_bio": self.cat_iv_bio,
        }

class Credit(db.Model):
    __tablename__ = "credits"
    id = db.Column(db.Integer, primary_key=True)
    pwp_name = db.Column(db.String(100), nullable=False)
    pwp_cpcb_reg_no = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False) # e.g., "Category II"
    tonnage_mt = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.String(20))
    purchase_cost = db.Column(db.Float)
    cpcb_ref_no = db.Column(db.String(100), unique=True)
    gst_invoice_no = db.Column(db.String(50))