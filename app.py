from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from evaluation import Evaluator
import numpy as np
import pprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///PathData.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO']=True

db = SQLAlchemy(app)

# render variable
eval_result_list = []

class PathTable(db.Model):
    __tablename__ = 'Path'
    id = db.Column(db.Integer, primary_key=True)
    PATH_TO_ANNOTATION_DIR = db.Column(db.Text)
    PATH_TO_INFER_RESULT = db.Column(db.Text)
    PATH_TO_TEST_LIST = db.Column(db.Text)

class ClassTable(db.Model):
    __tablename__ = 'Class'
    id = db.Column(db.Integer, primary_key=True)
    classname = db.Column(db.String(10))
    checked = db.Column(db.Boolean)
    iou = db.Column(db.Float)

@app.before_first_request
def init():
    db.create_all()

@app.route('/')
def initialize():
    global eval_result_list

    eval_result_list = []

    return redirect('/main')

@app.route('/main', methods=["GET"])
def reload():
    global eval_result_list

    class_list = []
    data = db.session.query(ClassTable)
    for classrow in data:
        class_list.append(classrow.classname)
        print(classrow.checked)
        print(classrow.iou)

    return render_template('main.html', eval_result_list=eval_result_list, class_list=class_list)

@app.route('/upload', methods=["GET"])
def upload():
    global eval_result_list

    eval_result_list = []
    path_to_annnotation_dir = request.args.get("gt")
    path_to_infer_result = request.args.get("infer")
    path_to_test_list = request.args.get("testlist")
    class_list = request.args.get("label").split(',')

    data = db.session.query(PathTable).first()
    data.PATH_TO_ANNOTATION_DIR = path_to_annnotation_dir
    data.PATH_TO_INFER_RESULT = path_to_infer_result
    data.PATH_TO_TEST_LIST = path_to_test_list

    db.session.query(ClassTable).delete()
    for classname in class_list:
        classrow = ClassTable(classname=classname, checked=True, iou=0.5)
        db.session.add(classrow)

    db.session.commit()

    return redirect('/main')

@app.route('/result', methods=["GET"])
def result():
    global eval_result_list

    data = db.session.query(PathTable).first()
    PATH_TO_ANNOTATION_DIR = data.PATH_TO_ANNOTATION_DIR
    PATH_TO_INFER_RESULT = data.PATH_TO_INFER_RESULT
    PATH_TO_TEST_LIST = data.PATH_TO_TEST_LIST

    class_list = []
    data = db.session.query(ClassTable)
    for classrow in data:
        class_list.append(classrow.classname)

    checklist = request.args.getlist("check")
    ioulist = request.args.getlist("iou")

    EVAL_TARGET_LIST = []
    for i, classname in enumerate(class_list):
        data = db.session.query(ClassTable).filter(ClassTable.classname==classname).first()
        if classname in checklist:
            data.checked = True
            data.iou = float(ioulist[i])
            dic = {'classname':classname, 'iou_th':float(ioulist[i])}
            EVAL_TARGET_LIST.append(dic)
        else:
            data.checked = False
            data.iou = float(ioulist[i])
        db.session.commit()

    SCORE_INCRIMENT = float(request.args.get("princ"))

    evaluator = Evaluator()
    evaluator.readInfer(PATH_TO_INFER_RESULT)
    evaluator.readGT(PATH_TO_ANNOTATION_DIR, PATH_TO_TEST_LIST)

    eval_result_list = []
    for eval_target in EVAL_TARGET_LIST:
        dic = {}
        eval_result, best_score = evaluator.evaluate(eval_target['classname'], eval_target['iou_th'], SCORE_INCRIMENT)
        dic['classname'] = eval_target['classname']
        dic['eval_result'] = eval_result
        dic['best_score'] = best_score
        eval_result_list.append(dic)

    return redirect('/main')

if __name__ == "__main__":
    app.run(debug=True)