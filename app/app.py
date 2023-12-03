from flask import Flask, render_template, request, redirect, jsonify, send_from_directory, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from evaluation import Evaluator

import xml.etree.ElementTree as ET
import csv
import json

import cv2
import numpy as np
from object_detection.utils import visualization_utils

app = Flask(__name__, static_folder='./static', template_folder='./templates')
DATASETS_DIR = './datasets/GTA5'
TEMP_IMAGE_PATH = 'C:/Users/Ryu/Documents/10_tech/10_object_detection/object_detection_evaluation_app/app/tmp/temp_image.jpg'

CORS(app)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///Data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO']=False

db = SQLAlchemy(app)

class GtList(db.Model):
    __tablename__ = 'gt_list'
    gt_id = db.Column(db.Integer, primary_key=True)
    gt_name = db.Column(db.String(30))
    gt_object = db.relationship('GtObject', backref='gt')

class GtObject(db.Model):
    __tablename__ = 'gt_obj'
    obj_id = db.Column(db.Integer, primary_key=True)
    gt_id = db.Column(db.Integer, db.ForeignKey('gt_list.gt_id'))
    file_name = db.Column(db.Text)
    class_name = db.Column(db.Text)
    left = db.Column(db.Integer)
    right = db.Column(db.Integer)
    top = db.Column(db.Integer)
    bottom = db.Column(db.Integer)

class InferList(db.Model):
    __tablename__ = 'infer_list'
    infer_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(30))
    infer_object = db.relationship('InferObject', backref='infer')

class InferObject(db.Model):
    __tablename__ = 'infer_obj'
    obj_id = db.Column(db.Integer, primary_key=True)
    infer_id = db.Column(db.Integer, db.ForeignKey('infer_list.infer_id'))
    file_name = db.Column(db.Text)
    class_name = db.Column(db.Text)
    left = db.Column(db.Integer)
    right = db.Column(db.Integer)
    top = db.Column(db.Integer)
    bottom = db.Column(db.Integer)
    score = db.Column(db.Float)

@app.before_first_request
def init():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getList', methods=["GET"])
def getGtInferList():
    data = db.session.query(GtList).all()
    gt_list = [{'gt_id': gt_info.gt_id, 'gt_name': gt_info.gt_name} for gt_info in data]
    data = db.session.query(InferList).all()
    infer_list = [{'infer_id': infer_info.infer_id, 'model_name': infer_info.model_name} for infer_info in data]
    return jsonify(gt_list=gt_list, infer_list=infer_list)

@app.route('/addGt', methods=["POST"])
def addGt():
    gt_name = request.form.get('gt_name')
    new_gt = GtList(gt_name=gt_name)
    db.session.add(new_gt)
    db.session.commit()

    gt_files = request.files.getlist('gt_files[]')
    for gt_file in gt_files:
        root = ET.parse(gt_file).getroot()
        for child in root:
            if child.tag == 'filename':
                file_name = child.text
            if child.tag == 'object':
                for tag in child:
                    if tag.tag=='name': class_name = tag.text
                    if tag.tag=='bndbox':
                        for bbox in tag:
                            if bbox.tag=='xmin': left = bbox.text
                            if bbox.tag=='xmax': right = bbox.text
                            if bbox.tag=='ymin': top = bbox.text
                            if bbox.tag=='ymax': bottom = bbox.text
                new_obj = GtObject(gt=new_gt,
                                   file_name=file_name,
                                   class_name=class_name,
                                   left=left, right=right,
                                   top=top,
                                   bottom=bottom)
                db.session.add(new_obj)
    db.session.commit()

    return jsonify({'message': 'succeed'})

@app.route('/addInfer', methods=["POST"])
def addInfer():
    model_name = request.form.get('model_name')
    new_infer = InferList(model_name=model_name)
    db.session.add(new_infer)
    db.session.commit()

    infer_file = request.files.get('infer_file')
    infer_file_contents = infer_file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(infer_file_contents)
    infered_objs = [row for row in reader]
    for obj in infered_objs:
        new_obj = InferObject(infer=new_infer,
                              file_name=obj['filename'],
                              class_name=obj['class'],
                              left=obj['left'],
                              right=obj['right'],
                              top=obj['top'],
                              bottom=obj['bottom'],
                              score=obj['score'])
        db.session.add(new_obj)
    db.session.commit()

    return jsonify({'message': 'succeed'})

@app.route('/deleteList', methods=["GET"])
def deleteList():
    table_name, delete_id = request.args.get("delete_info").split('_')
    if table_name == 'gt':
        db.session.query(GtObject).filter_by(gt_id=delete_id).delete()
        db.session.query(GtList).filter_by(gt_id=delete_id).delete()
        db.session.commit()
    elif table_name == 'infer':
        db.session.query(InferObject).filter_by(infer_id=delete_id).delete()
        db.session.query(InferList).filter_by(infer_id=delete_id).delete()
        db.session.commit()

    return jsonify({'message': 'succeed'})

@app.route('/getEval', methods=["GET"])
def getEval():
    gt_id = request.args.get("gt_id")
    infer_id = request.args.get("infer_id")
    class_iou_list = request.args.get('class_iou_list')
    class_iou_list = json.loads(class_iou_list) #class_name, iou_th

    evaluator = Evaluator()
    data = db.session.query(GtObject).filter_by(gt_id=gt_id).all()
    evaluator.gtlist = [{'filename': obj.file_name,
                         'class': obj.class_name,
                         'left': obj.left,
                         'right': obj.right,
                         'top': obj.top,
                         'bottom': obj.bottom} for obj in data]
    data = db.session.query(InferObject).filter_by(infer_id=infer_id).all()
    evaluator.inferlist = [{'filename': obj.file_name,
                         'class': obj.class_name,
                         'left': obj.left,
                         'right': obj.right,
                         'top': obj.top,
                         'bottom': obj.bottom,
                         'score': obj.score} for obj in data]

    if class_iou_list[0]['class_name']=='all':
        classes = list(set([obj['class'] for obj in evaluator.gtlist]))
        class_iou_list=[{'class_name':class_name, 'iou_th':0.5} for class_name in classes]

    eval_result_list = []
    for eval_target in class_iou_list:
        eval_result, best_score = evaluator.evaluate(eval_target['class_name'], float(eval_target['iou_th']), 0.01)
        eval_result_list.append({'class_name':eval_target['class_name'], 'best_score':best_score, 'eval_result':eval_result})

    return jsonify(eval_result_list=eval_result_list)

@app.route('/getImage', methods=["GET"])
def getImage():
    filename = request.args.get("filename")
    image_path = DATASETS_DIR + '/image/' + filename
    gt_id = request.args.get("gt_id")
    infer_id = request.args.get("infer_id")
    inspection_score = request.args.get("inspection_score")
    inspection_class_name = request.args.get("inspection_class_name")

    gt_data = db.session.query(GtObject).filter(
        GtObject.gt_id == gt_id,
        GtObject.file_name == filename,
        GtObject.class_name == inspection_class_name)
    
    infer_data = db.session.query(InferObject).filter(
        InferObject.infer_id == infer_id,
        InferObject.file_name == filename,
        InferObject.score >= inspection_score,
        InferObject.class_name == inspection_class_name)

    image_np = np.array(cv2.imread(image_path))

    image_np_with_detections = image_np.copy()
    height = image_np.shape[0]
    width = image_np.shape[1]

    detections = {'detection_boxes' : [],
                'detection_classes' : [],
                'detection_scores' : []}

    # 56 is lightgreen, 100 is red.
    category_index = {56: {'id': 56, 'name': 'GT'}, 100: {'id': 100, 'name': inspection_class_name}}

    for obj in gt_data:
        detections['detection_boxes'].append([obj.top/height, obj.left/width, obj.bottom/height, obj.right/width])
        detections['detection_classes'].append(56)
        detections['detection_scores'].append(1)

    for obj in infer_data:
        detections['detection_boxes'].append([obj.top/height, obj.left/width, obj.bottom/height, obj.right/width])
        detections['detection_classes'].append(100)
        detections['detection_scores'].append(obj.score)

    visualization_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            np.array(detections['detection_boxes']),
            np.array(detections['detection_classes']),
            np.array(detections['detection_scores']),
            category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=0,
            agnostic_mode=False)
        
    cv2.imwrite(TEMP_IMAGE_PATH, image_np_with_detections)

    return send_file(TEMP_IMAGE_PATH, mimetype='image/jpeg')

if __name__=='__main__':
    app.run(debug=True)