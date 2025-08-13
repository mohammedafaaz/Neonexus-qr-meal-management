from flask import render_template, request, jsonify, flash, redirect, url_for
from app import app
from extensions import db, mail
from models import QRCode, Session
from utils import generate_qr_code, send_qr_email, send_combined_qr_email, validate_qr_payload
from sqlalchemy import func
import json
import logging

@app.route('/')
def index():
    """Home page with navigation options"""
    return render_template('index.html')

@app.route('/admin')
def admin():
    """Admin dashboard"""
    sessions = Session.query.all()
    
    # Calculate statistics
    total_qr_codes = QRCode.query.count()
    redeemed_qr_codes = QRCode.query.filter_by(is_redeemed=True).count()
    remaining_qr_codes = total_qr_codes - redeemed_qr_codes
    
    stats = {
        'total': total_qr_codes,
        'redeemed': redeemed_qr_codes,
        'remaining': remaining_qr_codes
    }
    
    return render_template('admin.html', sessions=sessions, stats=stats)

@app.route('/scanner')
def scanner():
    """QR Scanner page"""
    sessions = Session.query.all()
    
    # Get recent redemptions (last 10)
    recent_redemptions = QRCode.query.filter_by(is_redeemed=True)\
                                   .order_by(QRCode.redeemed_at.desc())\
                                   .limit(10).all()
    
    return render_template('scanner.html', sessions=sessions, recent_redemptions=recent_redemptions)

@app.route('/api/create_session', methods=['POST'])
def create_session():
    """Create a new meal session"""
    try:
        session_name = request.form.get('session_name', '').strip()
        
        if not session_name:
            return jsonify({'success': False, 'message': 'Session name is required'})
        
        # Check if session already exists
        existing_session = Session.query.filter_by(name=session_name).first()
        if existing_session:
            return jsonify({'success': False, 'message': 'Session already exists'})
        
        # Create new session
        new_session = Session(name=session_name)
        db.session.add(new_session)
        db.session.commit()
        
        logging.info(f"Created session: {session_name}")
        return jsonify({'success': True, 'message': f'Session "{session_name}" created successfully'})
        
    except Exception as e:
        logging.error(f"Error creating session: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to create session'})

@app.route('/api/send_qr', methods=['POST'])
def send_qr():
    """Send QR code to participant email"""
    try:
        selected_sessions = request.form.getlist('selected_sessions')
        participant_email = request.form.get('participant_email', '').strip()
        
        if not participant_email:
            return jsonify({'success': False, 'message': 'Participant email is required'})
        
        if not selected_sessions:
            return jsonify({'success': False, 'message': 'Please select at least one session'})
        
        # Generate QR codes for all selected sessions
        qr_data_list = []
        qr_codes_to_add = []
        
        for session_name in selected_sessions:
            session = Session.query.filter_by(name=session_name).first()
            if not session:
                continue
            
            # Check if QR already exists for this session and email
            existing_qr = QRCode.query.filter_by(session_name=session_name, 
                                                participant_email=participant_email).first()
            if existing_qr:
                logging.warning(f"QR already exists for {participant_email} in session {session_name}")
                continue
            
            # Generate QR code
            qr_id = QRCode.generate_id(session_name)
            qr_payload = {
                'id': qr_id,
                'session': session_name,
                'email': participant_email,
                'keyword': 'NEON36'
            }
            
            # Create QR code record
            qr_code = QRCode(
                id=qr_id,
                session_name=session_name,
                participant_email=participant_email,
                qr_payload=json.dumps(qr_payload)
            )
            qr_codes_to_add.append(qr_code)
            
            # Generate QR image
            qr_image_path = generate_qr_code(qr_payload, qr_id)
            qr_data_list.append({
                'session_name': session_name,
                'qr_image_path': qr_image_path
            })
        
        # Send single email with all QR codes
        if qr_data_list and send_combined_qr_email(participant_email, qr_data_list):
            # Add all QR codes to database
            for qr_code in qr_codes_to_add:
                db.session.add(qr_code)
                logging.info(f"Added QR for session {qr_code.session_name} to {participant_email}")
            db.session.commit()
            sent_count = len(qr_codes_to_add)
        else:
            logging.error(f"Failed to send combined QR email to {participant_email}")
            sent_count = 0
        
        if sent_count > 0:
            return jsonify({'success': True, 'message': f'Sent {sent_count} QR code(s) successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send QR codes'})
            
    except Exception as e:
        logging.error(f"Error sending QR codes: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to send QR codes'})

@app.route('/api/validate_qr', methods=['POST'])
def validate_qr():
    """Validate and redeem QR code"""
    try:
        qr_data = request.json.get('qr_data')
        selected_session = request.json.get('selected_session')
        
        if not qr_data or not selected_session:
            return jsonify({
                'success': False, 
                'message': 'QR data and session selection required',
                'audio': 'failure'
            })
        
        # Validate QR payload
        is_valid, qr_payload = validate_qr_payload(qr_data)
        if not is_valid:
            return jsonify({
                'success': False, 
                'message': 'Invalid QR code format or missing NEON36 keyword',
                'audio': 'failure'
            })
        
        # Check if QR belongs to selected session
        if qr_payload.get('session') != selected_session:
            return jsonify({
                'success': False, 
                'message': f'QR code does not belong to session "{selected_session}"',
                'audio': 'failure'
            })
        
        # Find QR in database
        qr_code = QRCode.query.filter_by(id=qr_payload.get('id')).first()
        if not qr_code:
            return jsonify({
                'success': False, 
                'message': 'QR code not found in database',
                'audio': 'failure'
            })
        
        # Check if already redeemed
        if qr_code.is_redeemed:
            return jsonify({
                'success': False, 
                'message': f'QR code already redeemed on {qr_code.redeemed_at.strftime("%Y-%m-%d %H:%M:%S")}',
                'audio': 'failure'
            })
        
        # Redeem QR code
        if qr_code.redeem():
            db.session.commit()
            logging.info(f"Redeemed QR code: {qr_code.id}")
            return jsonify({
                'success': True, 
                'message': f'QR code redeemed successfully for {qr_code.participant_email}',
                'audio': 'success',
                'participant_email': qr_code.participant_email,
                'redeemed_at': qr_code.redeemed_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Failed to redeem QR code',
                'audio': 'failure'
            })
            
    except Exception as e:
        logging.error(f"Error validating QR code: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': 'Error processing QR code',
            'audio': 'failure'
        })

@app.route('/api/delete_all', methods=['POST'])
def delete_all():
    """Delete all sessions and QR codes"""
    try:
        # Delete all QR codes
        QRCode.query.delete()
        # Delete all sessions
        Session.query.delete()
        
        db.session.commit()
        logging.info("Deleted all sessions and QR codes")
        
        return jsonify({'success': True, 'message': 'All sessions and statistics deleted successfully'})
        
    except Exception as e:
        logging.error(f"Error deleting all data: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete all data'})

@app.route('/api/get_recent_redemptions')
def get_recent_redemptions():
    """Get recent redemptions for scanner page"""
    try:
        recent_redemptions = QRCode.query.filter_by(is_redeemed=True)\
                                       .order_by(QRCode.redeemed_at.desc())\
                                       .limit(10).all()
        
        redemptions_data = []
        for qr in recent_redemptions:
            redemptions_data.append({
                'id': qr.id,
                'session_name': qr.session_name,
                'participant_email': qr.participant_email,
                'redeemed_at': qr.redeemed_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return jsonify({'success': True, 'redemptions': redemptions_data})
        
    except Exception as e:
        logging.error(f"Error getting recent redemptions: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get recent redemptions'})

@app.route('/api/get_stats')
def get_stats():
    """Get current statistics"""
    try:
        total_qr_codes = QRCode.query.count()
        redeemed_qr_codes = QRCode.query.filter_by(is_redeemed=True).count()
        remaining_qr_codes = total_qr_codes - redeemed_qr_codes
        
        stats = {
            'total': total_qr_codes,
            'redeemed': redeemed_qr_codes,
            'remaining': remaining_qr_codes
        }
        
        return jsonify({'success': True, 'stats': stats})
        
    except Exception as e:
        logging.error(f"Error getting stats: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to get statistics'})
