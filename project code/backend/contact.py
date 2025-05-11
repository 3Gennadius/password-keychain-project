import re
import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import current_user
from flask_mail import Message
from . import mail, csrf, limiter
from .validation import validate_contact

contact_bp = Blueprint('contact', __name__, url_prefix='/contact')

FE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

@contact_bp.route('', methods=['GET'])
def contact_get():
    """Serve the contact form page directly."""
    return send_from_directory(FE, 'contact.html')


@contact_bp.route('/send-message', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per hour")
def contact_send():
    """
    Handle form submission.
    - Sanitizes & validates via validate_contact().
    - If logged in, uses current_user.username/email.
    - Otherwise uses supplied name/email.
    - Sends support email + auto-reply.
    """
    data = request.get_json() or {}
    form_name    = data.get('name', '').strip()
    form_email   = data.get('email', '').strip()
    message_text = data.get('message', '').strip()

    # Server-side validation
    errors = validate_contact(form_name, form_email, message_text)
    if errors:
        return jsonify(errors=errors), 400

    # Determine which name/email to use
    if current_user.is_authenticated:
        user_name  = current_user.username
        user_email = current_user.email
    else:
        user_name  = form_name
        user_email = form_email

    # Build the support email body
    body_lines = []
    if current_user.is_authenticated:
        body_lines.append(f"User ID: {current_user.user_id}")
        body_lines.append(f"Username: {current_user.username}")
        body_lines.append(f"Registered Email: {current_user.email}")
        body_lines.append("")  # blank line

    body_lines.append(f"From: {user_name} <{user_email}>")
    body_lines.append("")
    body_lines.append("Message:")
    body_lines.append(message_text)
    full_body = "\n".join(body_lines)

    try:
        # Send to support team
        support_msg = Message(
            subject=f"Support request from {user_name}",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[current_app.config['MAIL_USERNAME']],
            body=full_body
        )
        mail.send(support_msg)

        # Auto-reply to user
        auto_reply = Message(
            subject="We've received your message",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user_email],
            body=(
                f"Hi {user_name},\n\n"
                "Thanks for contacting us. We've received your message and will respond shortly.\n\n"
                "— The Support Team"
            )
        )
        mail.send(auto_reply)
        return jsonify({
            'message': f"✅ {user_name}, your message has been sent! We'll be in touch shortly."
        }), 200

    except Exception as e:
        current_app.logger.error("Contact form error: %s", e)
        return jsonify({'error': 'Failed to send message.'}), 500
