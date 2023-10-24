import numpy as np

class Evaluator:
    def __init__(self):
        self.inferlist = []
        self.gtlist = []

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
                            candidates.append({'gt':gt, 'iou':iou})
                # choose one gt to pair with infer
                if len(candidates) == 0:
                    pairlist_infer.append({'infer':infer, 'gt':'none', 'iou':'none'})
                elif len(candidates) == 1:
                    pairlist_infer.append({'infer':infer, 'gt':candidates[0]['gt'], 'iou':candidates[0]['iou']})
                elif len(candidates) >= 2:
                    maxiou = 0
                    for index, candidate in enumerate(candidates):
                        if candidate['iou'] > maxiou:
                            maxindex = index
                            maxiou = candidate['iou']
                    pairlist_infer.append({'infer':infer, 'gt':candidates[maxindex]['gt'], 'iou':candidates[maxindex]['iou']})
        
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
                                candidates.append({'infer':infer, 'iou':iou})

                # choose one infer to pair with gt
                if len(candidates) == 0:
                    pairlist_GT.append({'gt':gt, 'infer':'none', 'iou':'none'})
                elif len(candidates) == 1:
                    pairlist_GT.append({'gt':gt, 'infer':candidates[0]['infer'], 'iou':candidates[0]['iou']})
                elif len(candidates) >= 2:
                    maxiou = 0
                    for index, candidate in enumerate(candidates):
                        if candidate['iou'] > maxiou:
                            maxindex = index
                            maxiou = candidate['iou']
                    pairlist_GT.append({'gt':gt, 'infer':candidates[maxindex]['infer'], 'iou':candidates[maxindex]['iou']})

        return(pairlist_GT)

    def ConfusionMatrix(self, pairlist_infer, pairlist_GT):
        # -----data structure
        # TP_infer : {"filename":["hoge1.jpg", "hoge2.jpg", "hoge3.jpg", ...], "num":30}
        #  * TP_gt, FP, FN are the same above.

        TP_infer = {'filename':[], 'num':0}
        TP_gt = {'filename':[], 'num':0}
        FP = {'filename':[], 'num':0}
        FN = {'filename':[], 'num':0}

        for pair in pairlist_infer:
            if pair['gt'] != 'none':
                TP_infer['filename'].append(pair['infer']['filename'])
                TP_infer['num'] += 1
            else:
                FP['filename'].append(pair['infer']['filename'])
                FP['num'] += 1
        
        for pair in pairlist_GT:
            if pair['infer'] != 'none':
                TP_gt['filename'].append(pair['gt']['filename'])
                TP_gt['num'] += 1
            else:
                FN['filename'].append(pair['gt']['filename'])
                FN['num'] += 1

        return(TP_infer, TP_gt, FP, FN)
    
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
            result['TP_infer'], result['TP_gt'], result['FP'], result['FN'] = self.ConfusionMatrix(pairlist_infer, pairlist_GT)
            result['precision'] = round(result['TP_infer']['num']/result['infers'], 3) if result['infers']!=0 else 0.00
            result['recall'] = round(result['TP_gt']['num']/result['gts'], 3) if result['gts']!=0 else 0.00
            f1 = round(2*result['precision']*result['recall']/(result['precision']+result['recall']), 3) if result['precision']!=0 and result['recall']!=0 else 0.00
            if f1 > best_f1:
                best_f1 = f1
                best_score = round(SCORE_TH, 2)
            result['f1'] = f1
            results.append(result)

        return results, best_score

if __name__ == '__main__':
    pass