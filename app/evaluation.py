import numpy as np
from collections import defaultdict
from tqdm import tqdm

class Evaluator:
    def __init__(self):
        self.inferlist = []
        self.gtlist = []

    def iou(self, a, b):
        # NumPyでベクトル化されたIoU計算
        ax_mn, ay_mn, ax_mx, ay_mx = a
        bx_mn, by_mn, bx_mx, by_mx = b

        inter_xmin = max(ax_mn, bx_mn)
        inter_ymin = max(ay_mn, by_mn)
        inter_xmax = min(ax_mx, bx_mx)
        inter_ymax = min(ay_mx, by_mx)

        inter_area = max(0, inter_xmax - inter_xmin + 1) * max(0, inter_ymax - inter_ymin + 1)
        a_area = (ax_mx - ax_mn + 1) * (ay_mx - ay_mn + 1)
        b_area = (bx_mx - bx_mn + 1) * (by_mx - by_mn + 1)

        union_area = a_area + b_area - inter_area
        return inter_area / union_area if union_area > 0 else 0

    def preprocess_lists(self, class_name, score_th):
        # クラス名とスコアしきい値でフィルタリング
        infer_filtered = [
            infer for infer in self.inferlist
            if infer['class'] == class_name and float(infer['score']) > score_th
        ]
        gt_filtered = [
            gt for gt in self.gtlist
            if gt['class'] == class_name
        ]
        return infer_filtered, gt_filtered

    def find_pairs(self, infer_filtered, gt_filtered, iou_th):
        # ファイルごとにグループ化
        infer_by_file = defaultdict(list)
        gt_by_file = defaultdict(list)
        for infer in infer_filtered:
            infer_by_file[infer['filename']].append(infer)
        for gt in gt_filtered:
            gt_by_file[gt['filename']].append(gt)

        pairlist_infer = []
        pairlist_gt = []

        for filename, infers in infer_by_file.items():
            gts = gt_by_file.get(filename, [])

            for infer in infers:
                infer_bbox = [infer['left'], infer['top'], infer['right'], infer['bottom']]
                candidates = [
                    {'gt': gt, 'iou': self.iou(infer_bbox, [gt['left'], gt['top'], gt['right'], gt['bottom']])}
                    for gt in gts
                    if self.iou(infer_bbox, [gt['left'], gt['top'], gt['right'], gt['bottom']]) > iou_th
                ]

                if candidates:
                    best_match = max(candidates, key=lambda x: x['iou'])
                    pairlist_infer.append({'infer': infer, 'gt': best_match['gt'], 'iou': best_match['iou']})
                else:
                    pairlist_infer.append({'infer': infer, 'gt': 'none', 'iou': 'none'})

        for gt in gt_filtered:
            gt_bbox = [gt['left'], gt['top'], gt['right'], gt['bottom']]
            candidates = [
                {'infer': infer, 'iou': self.iou(gt_bbox, [infer['left'], infer['top'], infer['right'], infer['bottom']])}
                for infer in infer_filtered
                if self.iou(gt_bbox, [infer['left'], infer['top'], infer['right'], infer['bottom']]) > iou_th
            ]

            if candidates:
                best_match = max(candidates, key=lambda x: x['iou'])
                pairlist_gt.append({'gt': gt, 'infer': best_match['infer'], 'iou': best_match['iou']})
            else:
                pairlist_gt.append({'gt': gt, 'infer': 'none', 'iou': 'none'})

        return pairlist_infer, pairlist_gt

    def ConfusionMatrix(self, pairlist_infer, pairlist_gt):
        TP_infer = {'filename': [], 'num': 0}
        TP_gt = {'filename': [], 'num': 0}
        FP = {'filename': [], 'num': 0}
        FN = {'filename': [], 'num': 0}

        for pair in pairlist_infer:
            if pair['gt'] != 'none':
                TP_infer['filename'].append(pair['infer']['filename'])
                TP_infer['num'] += 1
            else:
                FP['filename'].append(pair['infer']['filename'])
                FP['num'] += 1

        for pair in pairlist_gt:
            if pair['infer'] != 'none':
                TP_gt['filename'].append(pair['gt']['filename'])
                TP_gt['num'] += 1
            else:
                FN['filename'].append(pair['gt']['filename'])
                FN['num'] += 1

        return TP_infer, TP_gt, FP, FN

    def evaluate(self, class_name, iou_th, SCORE_INCREMENT):
        results = []
        best_score, best_f1 = 0, 0
        score_th_arr = np.arange(0.00, 1.00, SCORE_INCREMENT)

        for score_th in tqdm(score_th_arr):
            infer_filtered, gt_filtered = self.preprocess_lists(class_name, score_th)
            pairlist_infer, pairlist_gt = self.find_pairs(infer_filtered, gt_filtered, iou_th)
            
            TP_infer, TP_gt, FP, FN = self.ConfusionMatrix(pairlist_infer, pairlist_gt)

            precision = round(TP_infer['num'] / len(pairlist_infer), 3) if len(pairlist_infer) != 0 else 0.0
            recall = round(TP_gt['num'] / len(pairlist_gt), 3) if len(pairlist_gt) != 0 else 0.0
            f1 = round(2 * precision * recall / (precision + recall), 3) if precision > 0 and recall > 0 else 0.0

            if f1 > best_f1:
                best_f1 = f1
                best_score = round(score_th, 2)

            results.append({
                'score': round(score_th, 2),
                'infers': len(pairlist_infer),
                'gts': len(pairlist_gt),
                'TP_infer': TP_infer,
                'TP_gt': TP_gt,
                'FP': FP,
                'FN': FN,
                'precision': precision,
                'recall': recall,
                'f1': f1
            })

        return results, best_score

if __name__ == '__main__':
    pass
