import { createApp } from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import './plugins/viewer.css'
import VueViewer from '../node_modules/v-viewer'
import { loadFonts } from './plugins/webfontloader'

loadFonts()

const app = createApp(App)

app.use(vuetify)
app.use(VueViewer)
app.mount('#app')
