<template>
  <div class="container-fluid bg-dark text-white">
    <div class="row">
      <div class="col-sm-2">
        <FileUpload @clicked-Upload="clickedUpload"></FileUpload>
      </div>
      <div class="col-sm-3">
        <EvalSetting ref="evalsetting_component" :gt_id="gt_id" :infer_id="infer_id" :class_iou_list="class_iou_list" @clicked-evaluate="initEvaluateResult" @clicked-apply="applyEvaluateResult"></EvalSetting>
      </div>
      <div class="col-sm-7">
        <EvalResult ref="evalresult_component" :eval_result_list="eval_result_list"></EvalResult>
      </div>
    </div>
  </div>
</template>

<script>
import FileUpload from './components/FileUpload.vue'
import EvalSetting from './components/EvalSetting.vue'
import EvalResult from './components/EvalResult.vue'
import axios from 'axios';

export default {
  name: 'App',
  components: {
    FileUpload, EvalSetting, EvalResult
  },
  data() {
    return {
      gt_id: 0,
      infer_id: 0,
      class_iou_list: [],
      eval_result_list: [],
    }
  },

  methods: {
    clickedUpload(){
      this.$refs.evalsetting_component.getList();
    },
    applyEvaluateResult(init){
      const class_iou_list_true = this.class_iou_list.filter(class_iou => class_iou.checked === true);
      axios.get('http://localhost:5000/getEval', {
        params: {
          gt_id: this.gt_id,
          infer_id: this.infer_id,
          class_iou_list: JSON.stringify(class_iou_list_true),
        }
      })
      .then(response => {
        this.eval_result_list = response.data.eval_result_list;
        if(init){
          this.class_iou_list = this.eval_result_list.map(eval_result=>({class_name:eval_result.class_name, iou_th:0.5, checked:true}));
        }
        this.$refs.evalresult_component.drawChart(this.eval_result_list);
        console.log('succeeded /getEval');
      })
    },
    initEvaluateResult(new_gt_id, new_infer_id){
      this.gt_id = new_gt_id;
      this.infer_id = new_infer_id;
      this.class_iou_list = [{"class_name":"all", "iou_th":0, "checked":true}];
      this.applyEvaluateResult(true);
    },
  },
}
</script>