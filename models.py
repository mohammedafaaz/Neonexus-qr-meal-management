from datetime import datetime
import uuid
from extensions import db

class QRCode(db.Model):
    __tablename__ = 'qr_codes'
    
    id = db.Column(db.String(100), primary_key=True)  # Session-prefixed UUID
    session_name = db.Column(db.String(100), nullable=False)
    participant_email = db.Column(db.String(120), nullable=False)
    is_redeemed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    redeemed_at = db.Column(db.DateTime, nullable=True)
    qr_payload = db.Column(db.Text, nullable=False)  # JSON payload embedded in QR
    
    def __repr__(self):
        return f'<QRCode {self.id}>'
    
    @staticmethod
    def generate_id(session_name):
        """Generate session-prefixed UUID"""
        # Clean session name for ID
        clean_session = session_name.upper().replace(' ', '').replace('-', '')[:10]
        short_uuid = str(uuid.uuid4())[:8]
        return f"{clean_session}-{short_uuid}"
    
    def redeem(self):
        """Mark QR code as redeemed"""
        if self.is_redeemed:
            return False
        self.is_redeemed = True
        self.redeemed_at = datetime.utcnow()
        return True

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Session {self.name}>'
