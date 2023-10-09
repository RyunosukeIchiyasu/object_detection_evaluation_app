<template>
	<v-row class="flex-column pa-2">
		<h3>GT List</h3>
		<v-table fixed-header height="250px" class="bg-grey-darken-2 text-white">
			<thead>
				<tr>
					<th><GroundTruthUpload @clicked-Upload="getList"></GroundTruthUpload></th>
					<th>ID</th>
					<th>GT Name</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="gt in gt_list" :key="gt.gt_id">
					<td style="text-align: center;"><input v-model="selected_gt_id" class="form-check-input" type="radio" :value="gt.gt_id" :checked="gt_id === gt.gt_id"></td>
					<td>{{ gt.gt_id }}</td>
					<td>{{ gt.gt_name }}</td>
					<td style="text-align: center;"><v-icon icon="mdi mdi-trash-can" @click="deleteList('gt_'+gt.gt_id)"></v-icon></td>
				</tr>
			</tbody>
		</v-table>
	</v-row>
		
	<v-row class="flex-column pa-2">
		<h3>Infer List</h3>
		<v-table fixed-header height="250px" class="bg-grey-darken-2 text-white">
			<thead>
				<tr>
					<th><InferUpload @clicked-Upload="getList"></InferUpload></th>
					<th>ID</th>
					<th>Model Name</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="infer in infer_list" :key="infer.infer_id">
					<td style="text-align: center;"><input v-model="selected_infer_id" class="form-check-input" type="radio" :value="infer.infer_id" :checked="infer_id === infer.infer_id"></td>
					<td>{{ infer.infer_id }}</td>
					<td>{{ infer.model_name }}</td>
					<td style="text-align: center;"><v-icon icon="mdi mdi-trash-can" @click="deleteList('infer_'+infer.infer_id)"></v-icon></td>
				</tr>
			</tbody>
		</v-table>
		<input type="hidden" name="class_iou_list" value='[{"class_name":"all", "iou_th":0.5}]'>
		<v-btn variant="flat" color="blue" @click="getEvaluateResult()">Evaluate</v-btn>
	</v-row>
		
	<v-row class="flex-column pa-2">
		<h3>Threshold Setting</h3>
		<v-table fixed-header height="250px" class="bg-grey-darken-2 text-white">
			<thead>
				<tr>
				<th>Class</th>
				<th>IoU Threshold</th>
				<th></th>
				</tr>
			</thead>
			<tbody>
				<tr v-for="class_iou in class_iou_list" :key="class_iou.class_name" style="vertical-align: middle;">
				<td><v-switch small v-model="class_iou.checked" color="info" :label="class_iou.class_name" :value="true" hide-details :model-value="class_iou.checked"></v-switch></td>
				<td><input class="form-range" type="range" v-model="class_iou.iou_th" max="0.9" min="0.1" step="0.1" hide-details></td>
				<td>{{class_iou.iou_th}}</td>
				</tr>
			</tbody>
		</v-table>
		<v-btn variant="flat" color="blue" @click="updateClassIouList()">Apply</v-btn>
	</v-row>

</template>

<script>
import GroundTruthUpload from './cards/GroundTruthUpload_card.vue'
import InferUpload from './cards/InferUpload_card.vue'

import axios from 'axios';

export default {
  name: 'EvalSetting',
  components: {
    GroundTruthUpload, InferUpload
  },

  props: ['gt_id', 'infer_id', 'class_iou_list'],
  
  data() {
    return {
      selected_gt_id: null,
      selected_infer_id: null,
      gt_list: [],
      infer_list: [],
    };
  },

  methods: {
    getList(){
      axios.get('http://localhost:5000/getList')
      .then(response => {
        this.gt_list = response.data.gt_list;
        this.infer_list = response.data.infer_list;
        console.log('succeeded /getList');
      })
    },
    deleteList(value){
      axios.get('http://localhost:5000/deleteList', {
        params: {
          delete_info: value,
        }
      })
      .then(() => {
        console.log('succeeded /deleteList');
        this.getList()
      })
    },
    getEvaluateResult(){
      const new_gt_id = this.selected_gt_id;
      const new_infer_id = this.selected_infer_id;
      this.$emit('clicked-evaluate', new_gt_id, new_infer_id)
    },
    updateClassIouList(){
      this.$emit('clicked-apply', false);
    },
  },

  mounted(){
    this.getList();
  },
}
</script>
