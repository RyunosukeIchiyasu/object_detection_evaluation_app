import csv
import xml.etree.ElementTree as ET 
import numpy as np

class Evaluator:
    def __init__(self):
        self.inferlist = []
        self.gtlist = []

    def readInfer(self, PATH_TO_INFER_RESULT):
        with open(PATH_TO_INFER_RESULT) as f:
            reader = csv.DictReader(f)
            self.inferlist = [row for row in reader]
        for infer in self.inferlist:
            infer['filename']=infer['filename'].split('.')[0]

    def readGT(self, PATH_TO_ANNOTATION_DIR, PATH_TO_TEST_LIST):
        with open(PATH_TO_TEST_LIST, "r") as f:
            lines = f.read().splitlines()
        GT_PATHS = []
        for line in lines:
            GT_PATHS.append(PATH_TO_ANNOTATION_DIR + line.split('.')[0] + '.xml')
        
        for index, gt_path in enumerate(GT_PATHS):
            root = ET.parse(gt_path).getroot()
            for child in root:
                if child.tag == 'object':
                    gt = {}
                    gt['filename'] = gt_path.split('/')[-1].split('.')[0]
                    for tag in child:
                        if tag.tag=='name': gt['class'] = tag.text
                        if tag.tag=='bndbox':
                            for bbox in tag:
                                if bbox.tag=='xmin': gt['left'] = bbox.text
                                if bbox.tag=='xmax': gt['right'] = bbox.text
                                if bbox.tag=='ymin': gt['top'] = bbox.text
                                if bbox.tag=='ymax': gt['bottom'] = bbox.text
                    self.gtlist.append(gt)
        # pprint.pprint(self.gtlist)

    def iou(self, a, b):
        # input shape : a, b =[xmin, ymin, xmax, ymax]
        ax_mn, ay_mn, ax_mx, ay_mx = a[0], a[1], a[2], a[3]
        bx_mn, by_mn, bx_mx, by_mx = b[0], b[1], b[2], b[3]

        a_area = (ax_mx - ax_mn + 1) * (ay_mx - ay_mn + 1)
        b_area = (bx_mx - bx_mn + 1) * (by_mx - by_mn + 1)

        abx_mn = max(ax_mn, bx_mn)
        aby_mn = max(ay_mn, by_mn)
        abx_mx = min(ax_mx, bx_mx)
        aby_mx = min(ay_mx, by_mx)
        w = max(0, abx_mx - abx_mn + 1)
        h = max(0, aby_mx - aby_mn + 1)
        intersect = w*h

        iou = intersect / (a_area + b_area - intersect)
        return iou

    def findPairInferToGT(self, SCORE_TH, IOU_TH, CLASS_LIST):
        # search for candidates
        # condition : iou is more than 0 and being detected the same class
        pairlist_infer = []

        for infer in self.inferlist:
            if float(infer['score']) < SCORE_TH or infer['class'] not in CLASS_LIST:
                pass
            else:
                candidates = []
                for gt in self.gtlist:
                    if infer['filename'] == gt['filename']:
                        infer_bbox = [int(infer['left']), int(infer['top']), int(infer['right']), int(infer['bottom'])]
                        gt_bbox = [int(gt['left']), int(gt['top']), int(gt['right']), int(gt['bottom'])]
                        iou = self.iou(infer_bbox, gt_bbox)
                        if iou > IOU_TH and infer['class']==gt['class']:
                            candidate = {}
                            candidate['gt'] = gt
                            candidate['iou'] = iou
                            candidates.append(candidate)
                # choose one gt to pair with infer
                pair = {}
                pair['infer'] = infer
                if len(candidates) == 0:
                    pair['gt'] = 'none'
                    pair['iou'] = 'none'
                    pairlist_infer.append(pair)
                elif len(candidates) == 1:
                    pair['gt'] = candidates[0]['gt']
                    pair['iou'] = candidates[0]['iou']
                    pairlist_infer.append(pair)
                elif len(candidates) >= 2:
                    maxiou = 0
                    for index, candidate in enumerate(candidates):
                        if candidate['iou'] > maxiou:
                            maxindex = index
                            maxiou = candidate['iou']
                    pair['gt'] = candidates[maxindex]['gt']
                    pair['iou'] = candidates[maxindex]['iou']
                    pairlist_infer.append(pair)
        
        return(pairlist_infer)

    def findPairGTToInfer(self, SCORE_TH, IOU_TH, CLASS_LIST):
        # search for candidates
        # condition : iou is more than 0 and being detected the same class
        pairlist_GT = []

        for gt in self.gtlist:
            if gt['class'] not in CLASS_LIST:
                pass
            else:
                candidates = []
                for infer in self.inferlist:
                    if float(infer['score']) < SCORE_TH:
                        pass
                    else:
                        if gt['filename'] == infer['filename']:
                            gt_bbox = [int(gt['left']), int(gt['top']), int(gt['right']), int(gt['bottom'])]
                            infer_bbox = [int(infer['left']), int(infer['top']), int(infer['right']), int(infer['bottom'])]
                            iou = self.iou(gt_bbox, infer_bbox)
                            if iou > IOU_TH and gt['class']==infer['class']:
                                candidate = {}
                                candidate['infer'] = infer
                                candidate['iou'] = iou
                                candidates.append(candidate)

                # choose one infer to pair with gt
                pair = {}
                pair['gt'] = gt
                if len(candidates) == 0:
                    pair['infer'] = 'none'
                    pair['iou'] = 'none'
                    pairlist_GT.append(pair)
                elif len(candidates) == 1:
                    pair['infer'] = candidates[0]['infer']
                    pair['iou'] = candidates[0]['iou']
                    pairlist_GT.append(pair)
                elif len(candidates) >= 2:
                    maxiou = 0
                    for index, candidate in enumerate(candidates):
                        if candidate['iou'] > maxiou:
                            maxindex = index
                            maxiou = candidate['iou']
                    pair['infer'] = candidates[maxindex]['infer']
                    pair['iou'] = candidates[maxindex]['iou']
                    pairlist_GT.append(pair)

        return(pairlist_GT)

    def ConfusionMatrix(self, pairlist_infer, pairlist_GT):
        TP_infer, TP_gt = 0, 0
        for pair in pairlist_infer:
            if pair['gt'] != 'none':
                TP_infer += 1
        
        for pair in pairlist_GT:
            if pair['infer'] != 'none':
                TP_gt += 1
        
        return(TP_infer, TP_gt)
    
    def evaluate(self, CLASS_LIST, IOU_TH, SCORE_INCRIMENT):
        results = []
        best_score, best_f1 = 0, 0
        for SCORE_TH in np.arange(0.00, 1.00, SCORE_INCRIMENT):
            result = {}
            pairlist_infer = self.findPairInferToGT(SCORE_TH, IOU_TH, CLASS_LIST)
            pairlist_GT = self.findPairGTToInfer(SCORE_TH, IOU_TH, CLASS_LIST)
            result['score'] = round(SCORE_TH, 2)
            result['infers'] = len(pairlist_infer)
            result['gts'] = len(pairlist_GT)
            result['TP_infer'], result['TP_gt'] = self.ConfusionMatrix(pairlist_infer, pairlist_GT)
            result['precision'] = round(result['TP_infer']/result['infers'], 3) if result['infers']!=0 else 0.00
            result['recall'] = round(result['TP_gt']/result['gts'], 3) if result['gts']!=0 else 0.00
            f1 = round(2*result['precision']*result['recall']/(result['precision']+result['recall']), 3) if result['infers']!=0 and result['gts']!=0 else 0.00
            if f1 > best_f1:
                best_f1 = f1
                best_score = round(SCORE_TH, 2)
            result['f1'] = f1
            results.append(result)

        return results, best_score

if __name__ == '__main__':
    IOU_TH = 0.5
    PATH_TO_INFER_RESULT = "C:/work/infer/out/infer_results.csv"
    PATH_TO_ANNOTATION_DIR = "C:/work/infer/data/"
    PATH_TO_TEST_LIST = "C:/work/infer/data/test.txt"
    CLASS_LIST = ['person', 'car']
    
    evaluator = Evaluator()
    evaluator.readInfer(PATH_TO_INFER_RESULT)
    evaluator.readGT(PATH_TO_ANNOTATION_DIR, PATH_TO_TEST_LIST)
    results = []
    for SCORE_TH in np.arange(0.00, 1.00, 0.01):
        result = {}
        pairlist_infer = evaluator.findPairInferToGT(SCORE_TH, IOU_TH, CLASS_LIST)
        pairlist_GT = evaluator.findPairGTToInfer(SCORE_TH, IOU_TH, CLASS_LIST)
        result['score'] = SCORE_TH
        result['infers'] = len(pairlist_infer)
        result['gts'] = len(pairlist_GT)
        result['TP_infer'], result['TP_gt'] = evaluator.ConfusionMatrix(pairlist_infer, pairlist_GT)
        result['precision'] = round(result['TP_infer']/result['infers'], 3) if result['infers']!=0 else 0.00
        result['recall'] = round(result['TP_gt']/result['gts'], 3) if result['gts']!=0 else 0.00
        result['f1'] = round(2*result['precision']*result['recall']/(result['precision']+result['recall']), 3) if result['infers']!=0 and result['gts']!=0 else 0.00
        results.append(result)
        print(result)
    pass