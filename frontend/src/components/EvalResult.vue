<template>
  <v-row class="flex-column pa-1">
		<div style="display: flex; align-items: center;">
      <h4>Best Performance Score</h4>
      <v-tooltip text="Displaying the optimal score threshold used for deploying the model (to maximize F1) 
        and the model's performance under these conditions.">
				<template v-slot:activator="{ props }">
					<v-btn icon="mdi-information" variant="plain" v-bind="props">
						<v-icon icon="mdi-information" v-bind="props" color="#e39a39"></v-icon>
					</v-btn>
				</template>
			</v-tooltip>
    </div>
    <v-table fixed-header height="200px" density="compact" style="color: #504f5a;">
      <thead>
        <tr>
          <th>Class</th>
          <th>Best Score TH</th>
          <th>Precision</th>
          <th>Recall</th>
          <th>F1</th>
          <th>TP(Infer)</th>
          <th>TP(GT)</th>
          <th>FP</th>
          <th>FN</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="result in eval_result_list" :key="result.classname">
          <td>{{ result.class_name }}</td>
          <td>{{ result.best_score }}</td>
          <td>{{ findEvalResultByScore(result, result.best_score).precision }}</td>
          <td>{{ findEvalResultByScore(result, result.best_score).recall }}</td>
          <td>{{ findEvalResultByScore(result, result.best_score).f1 }}</td>
          <td @click="FilterImageList(result, result.best_score, 'TP_infer')">
            <u>{{ findEvalResultByScore(result, result.best_score).TP_infer.num }} obj</u>
          </td>
          <td @click="FilterImageList(result, result.best_score, 'TP_gt')">
            <u>{{ findEvalResultByScore(result, result.best_score).TP_gt.num }} obj</u>
          </td>
          <td @click="FilterImageList(result, result.best_score, 'FP')">
            <u>{{ findEvalResultByScore(result, result.best_score).FP.num }} obj</u>
          </td>
          <td @click="FilterImageList(result, result.best_score, 'FN')">
            <u>{{ findEvalResultByScore(result, result.best_score).FN.num }} obj</u>
          </td>
        </tr>
      </tbody>
    </v-table>
  </v-row>
  
  <v-row class="pa-0">
    <v-col lg="5" class="flex-column">
      <div style="display: flex; align-items: center;">
        <h4>PR Curve</h4>
        <v-tooltip text="Displaying the tradeoff between precision and recall for different threshold.">
          <template v-slot:activator="{ props }">
            <v-btn icon="mdi-information" variant="plain" v-bind="props">
              <v-icon icon="mdi-information" v-bind="props" color="#e39a39"></v-icon>
            </v-btn>
          </template>
        </v-tooltip>
      </div>
      <div style="width: 550px; height: 550px;"><canvas id="pr-chart"></canvas></div>
    </v-col>
    
    <v-col lg="7" class="flex-column">
      <div style="display: flex; align-items: center;">
        <h4>Image Inspection</h4>
        <v-tooltip text="Review each object(true positive, false positive, false negative) in the images.">
          <template v-slot:activator="{ props }">
            <v-btn icon="mdi-information" variant="plain" v-bind="props">
              <v-icon icon="mdi-information" v-bind="props" color="#e39a39"></v-icon>
            </v-btn>
          </template>
        </v-tooltip>
      </div>
      <div style="display: flex; justify-content: space-between; text-align: center;">
        <v-icon icon="mdi-page-first" @click="InspectionFirst()" />
        <v-icon icon="mdi-chevron-left" @click="InspectionPrevious()" />
        <v-icon icon="mdi-chevron-right" @click="InspectionNext()" />
        <v-icon icon="mdi-page-last" @click="InspectionLast()" />
      </div>
      <p v-if="inspection_filename_list.length == 0" style="line-height: 0.5;">
        ( select "xx obj" in the table ... )</p>
      <p v-if="inspection_filename_list.length > 0" style="line-height: 0.5;">
        ({{ current_page + 1 }} / {{ inspection_filename_list.length }}) {{ filename }}</p>
      <viewer :images="image_source">
        <v-img :src="image_source" :alt="filename"></v-img>
      </viewer>
    </v-col>
    
  </v-row>
  
  <v-row class="pa-1">
    <v-col lg="12" class="flex-column">
      <div style="display: flex; align-items: center;">
        <h4>Detail</h4>
        <v-tooltip text="Displaying all score threshold and the model's performance under these conditions.">
          <template v-slot:activator="{ props }">
            <v-btn icon="mdi-information" variant="plain" v-bind="props">
              <v-icon icon="mdi-information" v-bind="props" color="#e39a39"></v-icon>
            </v-btn>
          </template>
        </v-tooltip>
      </div>
      <div v-for="result in eval_result_list" :key="result.classname">
        <h5>Class : {{ result.class_name }}</h5>
        <v-table fixed-header height="200px" density="compact" style="color: #504f5a;">
          <thead>
            <tr>
              <th>Score TH</th>
              <th>Num of infer</th>
              <th>Num of GT</th>
              <th>TP(Infer)</th>
              <th>TP(GT)</th>
              <th>FP</th>
              <th>FN</th>
              <th>Precision</th>
              <th>Recall</th>
              <th>F1</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="index in result.eval_result" :key="index.score">
              <td>{{ index.score }}</td>
              <td>{{ index.infers }} obj</td>
              <td>{{ index.gts }} obj</td>
              <td @click="FilterImageList(result, index.score, 'TP_infer')">
                <u>{{ index.TP_infer.num }} obj</u>
              </td>
              <td @click="FilterImageList(result, index.score, 'TP_gt')">
                <u>{{ index.TP_gt.num }} obj</u>
              </td>
              <td @click="FilterImageList(result, index.score, 'FP')">
                <u>{{ index.FP.num }} obj</u>
              </td>
              <td @click="FilterImageList(result, index.score, 'FN')">
                <u>{{ index.FN.num }} obj</u>
              </td>
              <td>{{ index.precision }}</td>
              <td>{{ index.recall }}</td>
              <td>{{ index.f1 }}</td>
            </tr>
          </tbody>
        </v-table>
      </div>
    </v-col>
  </v-row>
    
  </template>

<script>
import Chart from 'chart.js/auto';
import axios from 'axios';

export default {
  name: 'EvalResult',
  
  props: ['eval_result_list', 'gt_id', 'infer_id'],

  data() {
    return {
      myChart: {},
      color_chart: [
        "#f06060", //red
        "#60f0b6", //lime green
        "#60ccf0", //light blue
        "#f0ee60", //yellow
        "#f0a860", //orange
        "#c5f060", //green
        "#6e60f0", //light purple
        "#f2b8dc" //pink
      ],
      options_chart: {
        scales: {
          x: {
            min: 0,
            max: 1,
            title: {
              display: true,
              text: 'Recall',
              color: 'white'
            },
            grid: {
              color: "white",
              lineWidth: "0.2"
            },
            ticks: {
              color: "white"
            }
          },
          y: {
            min: 0,
            max: 1,
            title: {
              display: true,
              text: 'Precision',
              color: 'white'
            },
            grid: {
              color: "white",
              lineWidth: "0.2"
            },
            ticks: {
              color: "white"
            }
          }
        },
        plugins: {
          legend: {
            labels: {
              color: "white",
            }
          }
        },
        maintainAspectRatio: false,
      },
      inspection_filename_list: [],
      inspection_score: 0,
      inspection_class_name: "",
      current_page: 0,
      filename: "",
      image_source: "",
    };
  },

  methods: {
    findEvalResultByScore(result, score) {
      return result.eval_result.find((result) => result.score === score);
    },

    FilterImageList(result, score, metrix){
      if(metrix == 'TP_infer'){
        this.inspection_filename_list = [...new Set(result.eval_result.find((result) => result.score === score).TP_infer.filename)];
        this.inspection_score = score;
        this.inspection_class_name = result.class_name;
      }
      else if(metrix == 'TP_gt'){
        this.inspection_filename_list = [...new Set(result.eval_result.find((result) => result.score === score).TP_gt.filename)];
        this.inspection_score = score;
        this.inspection_class_name = result.class_name;
      }
      else if(metrix == 'FP'){
        this.inspection_filename_list = [...new Set(result.eval_result.find((result) => result.score === score).FP.filename)];
        this.inspection_score = score;
        this.inspection_class_name = result.class_name;
      }
      else if(metrix == 'FN'){
        this.inspection_filename_list = [...new Set(result.eval_result.find((result) => result.score === score).FN.filename)];
        this.inspection_score = score;
        this.inspection_class_name = result.class_name;
      }
      this.InspectionFirst();
    },

    drawChart(new_eval_result_list){
      if(Object.keys(this.myChart).length > 0){
        this.myChart.destroy();
      }

      const datasets_chart = [];
      new_eval_result_list.forEach((result, i) => {
        const data = [];
        result.eval_result.forEach((result_each_score) => {
          if (result_each_score.recall != 0 || result_each_score.precision != 0) {
            data.push({ x: result_each_score.recall, y: result_each_score.precision });
          }
        });
        datasets_chart.push({
          label: result.class_name,
          data: data,
          pointBackgroundColor: this.color_chart[i % 6],
          borderColor: this.color_chart[i % 6],
          showLine: true,
        });
      });

      const ctx = document.getElementById('pr-chart');
      this.myChart = new Chart(ctx, {
        type: 'scatter',
        data: {datasets: datasets_chart},
        options: this.options_chart,
      });
    },

    InspectionFirst(){
      this.current_page = 0;
      this.filename = this.inspection_filename_list[this.current_page];
      this.getImage();
    },
    InspectionPrevious(){
      this.current_page = Math.max(0, this.current_page - 1);
      this.filename = this.inspection_filename_list[this.current_page];
      this.getImage();
    },
    InspectionNext(){
      this.current_page = Math.min(this.current_page + 1, this.inspection_filename_list.length - 1);
      this.filename = this.inspection_filename_list[this.current_page];
      this.getImage();
    },
    InspectionLast(){
      this.current_page = this.inspection_filename_list.length - 1;
      this.filename = this.inspection_filename_list[this.current_page];
      this.getImage();
    },

    getImage(){
      // axios.get('http://localhost:5000/getImage', {
      axios.get('/getImage', {
        params: {
          filename: this.filename,
          gt_id: this.gt_id,
          infer_id: this.infer_id,
          inspection_score: this.inspection_score,
          inspection_class_name: this.inspection_class_name,
        },
        responseType: 'arraybuffer',
      })
      .then(response => {
        const imageBlob = new Blob([response.data], { type: 'image/jpeg' });
        const imageUrl = URL.createObjectURL(imageBlob);

        this.image_source = imageUrl;

        console.log('succeeded /getImage');
      })
    },
  },

  mounted(){
  },
}
</script>