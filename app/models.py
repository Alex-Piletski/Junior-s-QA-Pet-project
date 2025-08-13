from app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    about = db.Column(db.Text)
    avatar = db.Column(db.String(255))  # путь/URL к аватарке

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"


