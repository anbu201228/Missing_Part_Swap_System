from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "alstom_secret_key" # Required for flashing messages

# Configuration
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# Database Model
class SwapRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_name = db.Column(db.String(100), nullable=False)
    project = db.Column(db.String(50))
    reason = db.Column(db.Text)
    installation_name = db.Column(db.String(100))
    part_no = db.Column(db.String(50))
    part_name = db.Column(db.String(100))
    from_ts = db.Column(db.String(50))
    fix_ts = db.Column(db.String(50))
    image = db.Column(db.String(100))
    date = db.Column(db.String(20))
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new', methods=['GET', 'POST'])
def new_request():
    if request.method == 'POST':
        try:
            # Secure Image Upload Handling
            image_name = ""
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    # Prepend timestamp to filename to prevent overwrites
                    image_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))

            # Database Entry
            new_entry = SwapRequest(
                requester_name=request.form.get('requester_name'),
                project=request.form.get('project'),
                reason=request.form.get('reason'),
                installation_name=request.form.get('installation_name'),
                part_no=request.form.get('part_no'),
                part_name=request.form.get('part_name'),
                from_ts=request.form.get('from_ts'),
                fix_ts=request.form.get('fix_ts'),
                image=image_name,
                date=request.form.get('date') if request.form.get('date') else datetime.now().strftime('%Y-%m-%d')
            )

            db.session.add(new_entry)
            db.session.commit()
            flash("Request submitted successfully!", "success")
            return redirect(url_for('view_requests'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('new_request'))

    return render_template('new_request.html')

@app.route('/requests')
def view_requests():
    # Show newest requests first
    data = SwapRequest.query.all()
    return render_template('view_requests.html', data=data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)