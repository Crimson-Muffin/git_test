import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
current_dir = os.path.dirname(os.path.abspath(__file__))
# Create Flask app and initialize database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


# Database models
class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    roll_number = db.Column(db.String, unique = True, nullable = False)
    first_name = db.Column(db.String, nullable = False)
    last_name = db.Column(db.String)
    courses = db.relationship('Course', secondary ='enrollments')

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    course_code = db.Column(db.String, unique = True, nullable = False)
    course_name = db.Column(db.String, nullable = False)
    course_description = db.Column(db.String)

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# Declating flask routes

@app.route('/', methods=['GET'])
def index():
    students = Student.query.all()
    if(students == []):
        return render_template('index1.html', students=students)
    else:
        return render_template('index.html', students=students)

@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        roll_number = request.form['roll']
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        courses = request.form.getlist('courses')

        # Checking if the student already exists
        existing_student = Student.query.filter_by(roll_number=roll_number).first()

        if existing_student:
            return render_template('student_exists.html')
        
        new_student = Student(roll_number = roll_number, first_name = first_name, last_name = last_name)
        db.session.add(new_student)
        db.session.commit()

        for course_id in courses:
            enrollment = Enrollment(estudent_id = new_student.student_id , ecourse_id = course_id)
            db.session.add(enrollment)

        db.session.commit()
        return redirect(url_for('index'))
    
    courses = Course.query.all()
    return render_template('create_student.html', courses=courses)

@app.route('/student/update/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    enrollment = Enrollment.query.filter_by(estudent_id = student_id).all()
    if request.method == 'POST':
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        courses = request.form.getlist('courses')

        student.first_name = first_name
        student.last_name = last_name

        # Deleting the previous enrollments
        for enroll in enrollment:
            db.session.delete(enroll)
        db.session.commit()

        # Adding the new enrollments

        for course_id in courses:
            enrollment = Enrollment(estudent_id = student_id, ecourse_id = course_id)
            db.session.add(enrollment)

        db.session.commit()
        return redirect(url_for('index'))
    
    courses = Course.query.all()
    return render_template('update_form.html', student=student, courses=courses)


@app.route('/student/<int:student_id>', methods=['GET'])
def student_details(student_id):
    student = Student.query.get_or_404(student_id)
    # enrollment = Enrollment.query.filter_by(estudent_id = student_id).all()
    enrollment = Enrollment.query.join(Course,Enrollment.ecourse_id==Course.course_id).add_columns(Course.course_id, Course.course_code, Course.course_name, Course.course_description).filter(Enrollment.estudent_id==student.student_id).all()
    return render_template('details.html', student=student, enrollment=enrollment)



if __name__ == "__main__":
# Run the app
    app.run()
    app.debug = True
