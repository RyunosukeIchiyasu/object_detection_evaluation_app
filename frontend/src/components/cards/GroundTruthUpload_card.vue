<template>
	<v-dialog v-model="dialog" persistent width="500">
		<template v-slot:activator="{ props }">
			<v-icon icon="mdi-upload" v-bind="props" color="#0D6EFD"></v-icon>
		</template>
		<v-card>
			<v-card-title>
				<span class="text-h5">Add Ground Truth</span>
			</v-card-title>
			<v-card-text>
				<v-container>
					<v-text-field v-model="gt_name" label="GT name" class="pa-md-4"></v-text-field>
					<v-file-input v-model="gt_files" multiple label="GT files"></v-file-input>
				</v-container>
			</v-card-text>
			<v-card-actions>
				<v-spacer></v-spacer>
				<v-btn color="#69a195" variant="text" @click="dialog = false">
					Close
				</v-btn>
				<v-btn color="#69a195" variant="text" @click="addGt(); dialog = false">
					Upload
				</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>
import axios from 'axios';

export default {
  name: 'GroundTruthUpload',

  data() {
    return {
      gt_name: '',
      gt_files: null,
      dialog: false,
    };
  },

  methods: {
    addGt(){
      const formData = new FormData();
      formData.append('gt_name', this.gt_name);
      for (let i = 0; i < this.gt_files.length; i++) {
        formData.append('gt_files[]', this.gt_files[i]);
      }
      // axios.post('http://localhost:5000/addGt', formData, {
      axios.post('/addGt', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then(() => {
        this.$emit('clicked-Upload')
        console.log('succeeded /addGt');
      })
    },
  },
}
</script>