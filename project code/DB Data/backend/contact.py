from flask import Blueprint, render_template, request, jsonify, current_app
from flask_mail import Mail, Message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from backend import csrf
import re

mail = Mail()
contact_bp = Blueprint('contact', __name__)
limiter = Limiter(key_func=get_remote_address)

@contact_bp.route('/contact', methods=['GET'])
def contact_get():
    return render_template('contact.html')

@contact_bp.route('/send-message', methods=['POST'])
@limiter.limit("5 per hour")
@csrf.exempt
def send_message():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    user_email = data.get("email", "").strip()
    message_body = data.get("message", "").strip()

    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    if len(name) > 100:
        return jsonify({'error': 'Name cannot exceed 100 characters.'}), 400
    if not message_body or len(message_body) > 400:
        return jsonify({'error': 'Message must be between 1 and 400 characters.'}), 400

    email_regex = r"[^@\\s]+@[^@\\s]+\\.[^@\\s]+"
    if not re.match(email_regex, user_email):
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    mail_username = current_app.config.get('MAIL_USERNAME')
    if not mail_username:
        return jsonify({'error': 'Email service not configured.'}), 500

    try:
        support_msg = Message(
            subject="New Contact Form Submission",
            sender=mail_username,
            recipients=["b00139dunkey@gmail.com"],
            body=f"Name: {name}\nFrom: {user_email}\n\n{message_body}"
        )
        mail.send(support_msg)

        auto_reply = Message(
            subject="We've received your message",
            sender=mail_username,
            recipients=[user_email],
            body=f"Hi {name},\n\nThanks for contacting us. We'll respond shortly.\n\n— The Team"
        )
        mail.send(auto_reply)

        return jsonify({'message': 'Thanks for your message! We’ll get back to you shortly.'}), 200

    except Exception as e:
        current_app.logger.error("Contact form error: %s", e)
        return jsonify({'error': 'Failed to send message.'}), 500
