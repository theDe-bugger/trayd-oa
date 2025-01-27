from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    customer = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('In Progress', 'Completed', name='job_status'), nullable=True)
    workers = db.relationship('Worker', backref='job', lazy=True)

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=True)

# Initialize database
with app.app_context():
    db.create_all()

# Helper Functions
def parse_date(date_str, error_message):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

def format_job(job):
    return {
        'id': job.id,
        'name': job.name,
        'customer': job.customer,
        'startDate': job.start_date.strftime('%Y-%m-%d') if job.start_date else None,
        'endDate': job.end_date.strftime('%Y-%m-%d') if job.end_date else None,
        'status': job.status,
        'workerCount': len(job.workers)
    }

def format_worker(worker):
    return {
        'id': worker.id,
        'name': worker.name,
        'role': worker.role,
        'jobId': worker.job_id
    }

# Job Routes
@app.route('/jobs', methods=['POST'])
def create_job():
    try:
        data = request.get_json()
        if not data or not data.get('name') or not data.get('customer'):
            return jsonify({'error': 'Name and customer are required'}), 400

        start_date = parse_date(data.get('startDate'), 'Invalid start date format')
        end_date = parse_date(data.get('endDate'), 'Invalid end date format')
        
        status = data.get('status')
        if status and status not in ['In Progress', 'Completed']:
            return jsonify({'error': 'Invalid status'}), 400

        new_job = Job(
            name=data['name'],
            customer=data['customer'],
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        db.session.add(new_job)
        db.session.commit()
        
        return jsonify(format_job(new_job)), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/jobs', methods=['GET'])
def get_jobs():
    try:
        query = Job.query
        
        # Apply filters
        if search_name := request.args.get('name'):
            query = query.filter(Job.name.ilike(f'%{search_name}%'))
        if search_customer := request.args.get('customer'):
            query = query.filter(Job.customer.ilike(f'%{search_customer}%'))
        if status := request.args.get('status'):
            query = query.filter(Job.status == status)
        if start_after := request.args.get('startAfter'):
            start_date = parse_date(start_after, 'Invalid start_after date')
            if start_date:
                query = query.filter(Job.start_date >= start_date)
        if end_before := request.args.get('endBefore'):
            end_date = parse_date(end_before, 'Invalid end_before date')
            if end_date:
                query = query.filter(Job.end_date <= end_date)

        # Apply sorting
        sort_by = request.args.get('sortBy', 'id')
        if sort_by in ['name', 'customer', 'start_date', 'end_date', 'status']:
            sort_column = getattr(Job, sort_by)
            if request.args.get('order') == 'desc':
                sort_column = sort_column.desc()
            query = query.order_by(sort_column)

        # Handle pagination
        page = request.args.get('page', type=int)
        per_page = request.args.get('limit', type=int)

        if page and per_page:
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            response = {
                'jobs': [format_job(job) for job in pagination.items],
                'pagination': {
                    'page': page,
                    'perPage': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        else:
            response = {'jobs': [format_job(job) for job in query.all()]}
            
        return jsonify(response)
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return '', 204
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# Worker Routes
@app.route('/workers', methods=['POST'])
def create_worker():
    try:
        data = request.get_json()
        if not data or not data.get('name') or not data.get('role'):
            return jsonify({'error': 'Name and role are required'}), 400
        
        worker = Worker(
            name=data['name'],
            role=data['role'],
            job_id=data.get('jobId')
        )
        db.session.add(worker)
        db.session.commit()
        
        return jsonify(format_worker(worker)), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/workers/bulk', methods=['POST'])
def bulk_create_workers():
    try:
        workers_data = request.get_json()
        if not isinstance(workers_data, list):
            return jsonify({'error': 'Invalid data format. Expected array of workers'}), 400
        
        workers = []
        for data in workers_data:
            if not data.get('name') or not data.get('role'):
                return jsonify({'error': 'Name and role are required for all workers'}), 400
            
            worker = Worker(
                name=data['name'],
                role=data['role'],
                job_id=data.get('jobId')
            )
            db.session.add(worker)
            workers.append(worker)
        
        db.session.commit()
        return jsonify([format_worker(w) for w in workers]), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/workers', methods=['GET'])
def get_workers():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        query = Worker.query

        if name := request.args.get('name'):
            query = query.filter(Worker.name.ilike(f'%{name}%'))
        if role := request.args.get('role'):
            query = query.filter(Worker.role.ilike(f'%{role}%'))
        if job_id := request.args.get('jobId', type=int):
            query = query.filter(Worker.job_id == job_id)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'workers': [format_worker(w) for w in pagination.items],
            'pagination': {
                'page': page,
                'perPage': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/jobs/<int:job_id>/workers', methods=['GET'])
def get_job_workers(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        return jsonify([format_worker(w) for w in job.workers])
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        jobs_by_status = db.session.query(
            Job.status, 
            func.count(Job.id)
        ).group_by(Job.status).all()
        
        workers_by_role = db.session.query(
            Worker.role, 
            func.count(Worker.id)
        ).group_by(Worker.role).all()
        
        return jsonify({
            'jobs': {
                'total': Job.query.count(),
                'byStatus': {status: count for status, count in jobs_by_status if status}
            },
            'workers': {
                'total': Worker.query.count(),
                'byRole': dict(workers_by_role)
            }
        })
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
