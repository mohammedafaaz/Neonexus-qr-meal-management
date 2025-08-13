import qrcode
import json
import os
import tempfile
import logging
from flask_mail import Message
from app import mail
from PIL import Image, ImageDraw, ImageFont

def generate_qr_code(qr_payload, qr_id):
    """Generate QR code image with embedded JSON payload"""
    try:
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add JSON payload to QR code
        qr.add_data(json.dumps(qr_payload))
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        qr_image_path = os.path.join(temp_dir, f"qr_{qr_id}.png")
        img.save(qr_image_path)
        
        logging.info(f"Generated QR code: {qr_image_path}")
        return qr_image_path
        
    except Exception as e:
        logging.error(f"Error generating QR code: {str(e)}")
        return None

def send_qr_email(participant_email, session_name, qr_image_path):
    """Send QR code via email"""
    try:
        if not qr_image_path or not os.path.exists(qr_image_path):
            logging.error("QR image file not found")
            return False
        
        # Create email message
        subject = f"NEONEXUS36.0 - Meal QR Pass for {session_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: bold;">🚀 NEONEXUS36.0</h1>
                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">BITM IEEE STUDENT BRANCH</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <h2 style="color: #333; margin-top: 0;">Your Meal QR Pass is Ready!</h2>
                    
                    <p style="color: #555; line-height: 1.6;">Dear Participant,</p>
                    
                    <p style="color: #555; line-height: 1.6;">
                        Your QR pass for <strong>{session_name}</strong> session is attached to this email. 
                        Please save this QR code with the session name (Ex: DINNER DAY-1) and present it during the meal time for scanning.
                    </p>
                    
                    <!-- Important Instructions -->
                    <div style="background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <h3 style="color: #856404; margin-top: 0; font-size: 16px;">📋 Important Instructions:</h3>
                        <ul style="color: #856404; margin-bottom: 0;">
                            <li>This QR code is valid for <strong>ONE-TIME USE ONLY</strong></li>
                            <li>Present the QR code on your device or print it out</li>
                            <li>Each QR code is unique and non-transferable</li>
                            <li>Contact the organizers if you face any issues</li>
                        </ul>
                    </div>
                    
                    <p style="color: #555; line-height: 1.6;">
                        Get ready for an amazing 36-hour coding journey! 💻✨
                    </p>
                    
                    <p style="color: #555; line-height: 1.6;">
                        Best regards,<br>
                        <strong>Team NEONEXUS</strong><br>
                        BITM IEEE Student Branch
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                    <p style="margin: 0; color: #6c757d; font-size: 12px;">
                        This is an automated email for NEONEXUS36.0 hackathon participants. Please do not respond.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[participant_email],
            html=html_body
        )
        
        # Attach QR code image
        with open(qr_image_path, 'rb') as f:
            msg.attach(
                filename=f"{session_name}.png",
                content_type="image/png",
                data=f.read()
            )
        
        # Send email
        mail.send(msg)
        
        # Clean up temporary file
        try:
            os.remove(qr_image_path)
            logging.info(f"Cleaned up temporary QR file: {qr_image_path}")
        except:
            pass
        
        logging.info(f"Sent QR email to {participant_email} for session {session_name}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        # Clean up temporary file on error
        try:
            if qr_image_path and os.path.exists(qr_image_path):
                os.remove(qr_image_path)
        except:
            pass
        return False

def send_combined_qr_email(participant_email, qr_data_list):
    """Send all QR codes in a single email"""
    try:
        session_names = [data['session_name'] for data in qr_data_list]
        subject = f"🎟️ Your NEONEXUS36.0 Meal Passes - {', '.join(session_names)}"
        
        # Attach header image as attachment instead of embedding
        header_image_path = os.path.join('static', 'images', 'neonexus_header.jpg')
        
        # Create session list for email content
        session_list_html = ""
        for data in qr_data_list:
            session_list_html += f"<li><strong>{data['session_name']}</strong></li>"
        
        # HTML email template with embedded header image
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NEONEXUS36.0 QR Passes</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #6b46c1 0%, #9333ea 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: bold; letter-spacing: 2px;">NEONEXUS36.0</h1>
                    <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">BITM IEEE STUDENT BRANCH</p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    <h2 style="color: #333; margin-top: 0;">Your Meal QR Passes are Ready!</h2>
                    
                    <p style="color: #555; line-height: 1.6;">Dear Participant,</p>
                    
                    <p style="color: #555; line-height: 1.6;">
                        Your QR passes for the following sessions are attached to this email use in the same order:
                    </p>
                    
                    <ul style="color: #555; line-height: 1.6;">
                        {session_list_html}
                    </ul>
                    
                    <p style="color: #555; line-height: 1.6;">
                        Please save these QR codes with session name (e.g. DINNER DAY-1) and present them during the respective meal times for scanning.
                    </p>
                    
                    <!-- Important Instructions -->
                    <div style="background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <h3 style="color: #856404; margin-top: 0; font-size: 16px;">📋 Important Instructions:</h3>
                        <ul style="color: #856404; margin-bottom: 0;">
                            <li>Each QR code is valid for <strong>ONE-TIME USE ONLY</strong></li>
                            <li>Present the QR code on your device</li>
                            <li>Each QR code is unique and non-transferable</li>
                            <li>Contact the organizers if you face any issues</li>
                        </ul>
                    </div>
                    
                    <p style="color: #555; line-height: 1.6;">
                        All the best for the amazing 36-hour coding journey! 💻✨
                    </p>
                    
                    <p style="color: #555; line-height: 1.6;">
                        Best regards,<br>
                        <strong>Team NEONEXUS36.0</strong><br>
                        BITM IEEE Student Branch
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
                    <p style="margin: 0; color: #6c757d; font-size: 12px;">
                        This is an automated email for NEONEXUS36.0 hackathon participants. Please do not respond.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[participant_email],
            html=html_body
        )
        
        # Attach all QR code images
        for data in qr_data_list:
            qr_image_path = data['qr_image_path']
            session_name = data['session_name']
            
            with open(qr_image_path, 'rb') as f:
                msg.attach(
                    filename=f"{session_name}.png",
                    content_type="image/png",
                    data=f.read()
                )
        
        # Send email
        mail.send(msg)
        
        # Clean up temporary files
        for data in qr_data_list:
            try:
                os.remove(data['qr_image_path'])
                logging.info(f"Cleaned up temporary QR file: {data['qr_image_path']}")
            except:
                pass
        
        logging.info(f"Sent combined QR email to {participant_email} with {len(qr_data_list)} sessions")
        return True
        
    except Exception as e:
        logging.error(f"Error sending combined email: {str(e)}")
        # Clean up temporary files on error
        for data in qr_data_list:
            try:
                if os.path.exists(data['qr_image_path']):
                    os.remove(data['qr_image_path'])
            except:
                pass
        return False

def validate_qr_payload(qr_data):
    """Validate QR code payload"""
    try:
        # Parse JSON from QR data
        qr_payload = json.loads(qr_data)
        
        # Check required fields
        required_fields = ['id', 'session', 'email', 'keyword']
        for field in required_fields:
            if field not in qr_payload:
                logging.warning(f"Missing required field: {field}")
                return False, None
        
        # Validate keyword
        if qr_payload.get('keyword') != 'NEON36':
            logging.warning("Invalid keyword in QR payload")
            return False, None
        
        return True, qr_payload
        
    except json.JSONDecodeError:
        logging.warning("Invalid JSON in QR code")
        return False, None
    except Exception as e:
        logging.error(f"Error validating QR payload: {str(e)}")
        return False, None
