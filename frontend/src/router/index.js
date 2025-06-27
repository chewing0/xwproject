import { createRouter, createWebHistory } from 'vue-router'
import ModuleOneView from '../views/Module1.vue'
import ModuleTwoView from '../views/Module2.vue'
import ModuleThreeView from '../views/Module3.vue'

const routes = [
  {
    path: '/',
    redirect: '/module1'
  },
  {
    path: '/module1',
    name: 'Module1',
    component: ModuleOneView
  },
  {
    path: '/module2',
    name: 'Module2',
    component: ModuleTwoView
  },
  {
    path: '/module3',
    name: 'Module3',
    component: ModuleThreeView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router 