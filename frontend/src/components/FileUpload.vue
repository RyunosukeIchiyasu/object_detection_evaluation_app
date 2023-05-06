<template>
  <div>
    <h1 class="fs-4">Add Ground Truth</h1>
    <v-text-field v-model="gt_name" label="GT name" class="pa-md-4"></v-text-field>
    <v-file-input v-model="gt_files" multiple label="GT files"></v-file-input>
    <v-btn variant="flat" color="blue" @click="addGt()">Upload</v-btn>

    <h1 class="fs-4">Add Infer Result</h1>
    <v-text-field v-model="model_name" label="Model name"></v-text-field>
    <v-file-input v-model="infer_file" label="Infer File"></v-file-input>
    <v-btn variant="flat" color="blue" @click="addInfer()">Upload</v-btn>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'FileUpload',

  data() {
    return {
      gt_name: '',
      gt_files: null,
      model_name: '',
      infer_file: null,
    };
  },

  methods: {
    addGt(){
      const formData = new FormData();
      formData.append('gt_name', this.gt_name);
      for (let i = 0; i < this.gt_files.length; i++) {
        formData.append('gt_files[]', this.gt_files[i]);
      }
      axios.post('http://localhost:5000/addGt', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then(() => {
        this.$emit('clicked-Upload')
        console.log('succeeded /addGt');
      })
    },
    addInfer(){
      const formData = new FormData();
      formData.append('model_name', this.model_name);
      formData.append('infer_file', this.infer_file[0]);
      axios.post('http://localhost:5000/addInfer', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then(() => {
        this.$emit('clicked-Upload')
        console.log('succeeded /addInfer');
      })
    },
  },
}
</script>
