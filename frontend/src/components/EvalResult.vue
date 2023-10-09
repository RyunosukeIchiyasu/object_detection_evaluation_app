<template>
  <v-row class="flex-column pa-2">
    <h3>Best Performance</h3>
    <v-table fixed-header height="250px" class="bg-grey-darken-2 text-white">
      <thead>
        <tr>
          <th>Class</th>
          <th>Best Score</th>
          <th>Precision</th>
          <th>Recall</th>
          <th>F1</th>
          <th>TP_infer</th>
          <th>TP_gt</th>
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
          <td>{{ findEvalResultByScore(result, result.best_score).TP_infer }} obj</td>
          <td>{{ findEvalResultByScore(result, result.best_score).TP_gt }} obj</td>
          <td>{{ findEvalResultByScore(result, result.best_score).infers - findEvalResultByScore(result, result.best_score).TP_infer }} obj</td>
          <td>{{ findEvalResultByScore(result, result.best_score).gts - findEvalResultByScore(result, result.best_score).TP_gt }} obj</td>
        </tr>
      </tbody>
    </v-table>
  </v-row>
  
  <v-row class="pa-2">
    <v-col lg="6" class="flex-column">
      <h3>PR Curve</h3>
      <div style="width:500px;height:500px;"><canvas id="pr-chart"></canvas></div>
    </v-col>
    
    <v-col lg="6" class="flex-column">
      <h3>Detail</h3>
      <div v-for="result in eval_result_list" :key="result.classname" class="pa-2">
        <h5>{{ result.class_name }}: best score is {{ result.best_score }}</h5>
        <v-table fixed-header height="200px" class="bg-grey-darken-2 text-white">
          <thead>
            <tr>
              <th>Score</th>
              <th>infers</th>
              <th>Gts</th>
              <th>TP_infer</th>
              <th>TP_gt</th>
              <th>precision</th>
              <th>recall</th>
              <th>f1</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="index in result.eval_result" :key="index.score">
              <td>{{ index.score }}</td>
              <td>{{ index.infers }}</td>
              <td>{{ index.gts }}</td>
              <td>{{ index.TP_infer }}</td>
              <td>{{ index.TP_gt }}</td>
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

export default {
  name: 'EvalResult',
  
  props: ['eval_result_list'],

  data() {
    return {
      myChart: {},
      color_chart: ["lime", "aqua", "yellow", "red", "blue", "fuchsia"],
      options_chart: {
          scales: {
            x: {min: 0, max: 1, title: {display: true, text: 'Recall'}},
            y: {min: 0, max: 1, title: {display: true, text: 'Precision'}}
          },
          maintainAspectRatio: false,
        }
    };
  },

  methods: {
    findEvalResultByScore(result, score) {
      return result.eval_result.find((result) => result.score === score);
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
  },

  mounted(){
  },
}

</script>
