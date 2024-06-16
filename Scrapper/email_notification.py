from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Email configuration
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USERNAME = 'diverdial@gmail.com'
SMTP_PASSWORD = 'dialdiver2024'
EMAIL_FROM = 'diverdial@gmail.com'

def send_email(subject, recipient, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, recipient, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@app.route('/send_email', methods=['POST'])
def send_email_route():
    data = request.json
    subject = data.get('subject')
    recipient = data.get('recipient')
    body = data.get('body')

    if not subject or not recipient or not body:
        return jsonify({'error': 'Subject, recipient, and body are required'}), 400

    if send_email(subject, recipient, body):
        return jsonify({'message': 'Email sent successfully'}), 200
    else:
        return jsonify({'error': 'Failed to send email'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')