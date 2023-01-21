from flask import Flask
from flask import render_template, request, redirect
from evaluation import Evaluator
import numpy as np
import pprint

app = Flask(__name__)

# render variable
eval_result_list = []
class_list = []

# global variable
PATH_TO_ANNOTATION_DIR = None
PATH_TO_INFER_RESULT = None
PATH_TO_TEST_LIST = None

@app.route('/', methods=["GET"])
def index():
    global eval_result_list, class_list, PATH_TO_ANNOTATION_DIR, PATH_TO_INFER_RESULT, PATH_TO_TEST_LIST

    # eval_result_list = []
    # class_list = []
    # PATH_TO_ANNOTATION_DIR = None
    # PATH_TO_INFER_RESULT = None
    # PATH_TO_TEST_LIST = None

    return render_template('index.html', eval_result_list=eval_result_list, class_list=class_list)

@app.route('/upload', methods=["GET"])
def upload():
    global eval_result_list, class_list, PATH_TO_ANNOTATION_DIR, PATH_TO_INFER_RESULT, PATH_TO_TEST_LIST

    eval_result_list = []
    class_list = []
    PATH_TO_ANNOTATION_DIR = request.args.get("gt")
    PATH_TO_INFER_RESULT = request.args.get("infer")
    PATH_TO_TEST_LIST = request.args.get("testlist")
    class_list = request.args.get("label").split(',')

    return redirect('/')

    # return render_template('index.html', eval_result_list=eval_result_list, class_list=class_list)

@app.route('/result', methods=["GET"])
def result():
    global eval_result_list, class_list, PATH_TO_ANNOTATION_DIR, PATH_TO_INFER_RESULT, PATH_TO_TEST_LIST

    checklist = request.args.getlist("check")
    ioulist = request.args.getlist("iou")
    EVAL_TARGET_LIST = []
    for i, classname in enumerate(class_list):
        if classname in checklist:
            dic = {'classname':classname, 'iou_th':float(ioulist[i])}
            EVAL_TARGET_LIST.append(dic)
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

    return redirect('/')

    # return render_template('index.html', eval_result_list=eval_result_list, class_list=class_list)

if __name__ == "__main__":
    app.run(debug=True)