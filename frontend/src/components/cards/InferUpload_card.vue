<template>
	<v-dialog v-model="dialog" persistent width="500">
		<template v-slot:activator="{ props }">
			<v-icon icon="mdi-upload" v-bind="props" color="#0D6EFD"></v-icon>
		</template>
		<v-card>
			<v-card-title>
				<span class="text-h5">Add Infer Result</span>
			</v-card-title>
			<v-card-text>
				<v-container>
					<v-text-field v-model="model_name" label="Model name"></v-text-field>
					<v-file-input v-model="infer_file" label="Infer File"></v-file-input>
				</v-container>
			</v-card-text>
			<v-card-actions>
				<v-spacer></v-spacer>
				<v-btn color="#69a195" variant="text" @click="dialog = false">
					Close
				</v-btn>
				<v-btn color="#69a195" variant="text" @click="addInfer(); dialog = false">
					Upload
				</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>
import axios from 'axios';

export default {
  name: 'InferUpload',

  data() {
    return {
			model_name: '',
			infer_file: null,
			dialog: false,
    };
  },

  methods: {
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