import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SocialView from '../views/SocialView.vue'
import MatchView from '../views/MatchView.vue'
import MessagesView from '../views/MessagesView.vue'
import ProfileView from '../views/ProfileView.vue'
import AdminView from '../views/AdminView.vue'
import LoginView from '../views/LoginView.vue'
import { useAuthStore } from '../stores/authStore'
import ChangePswdView from '../views/ChangePswdView.vue'
import RegisterView from '../views/RegisterView.vue'
import CreateEventView from '../views/CreateEventView.vue'
import EditEventView from '../views/EditEventView.vue'
import CreateDraftView from '../views/CreateDraftView.vue'
import EditGroupView from '../views/EditGroupView.vue'
import CreateGroupView from '../views/CreateGroupView.vue'

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/social', name: 'Social', component: SocialView, meta: { requiresAuth: true } },
  { path: '/match', name: 'Match', component: MatchView, meta: { requiresAuth: true } },
  { path: '/messages', name: 'Messages', component: MessagesView, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: ProfileView, meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: AdminView, meta: { requiresAdmin: true } },
  { path: '/changePswd', name: 'ChangePswd', component: ChangePswdView },
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/create-event', name: 'CreateEvent', component: CreateEventView, meta: { requiresAuth: true } },
  { path: '/edit-event/:id', name: 'EditEvent', component: EditEventView, meta: { requiresAuth: true } },
  { path: '/create-draft/:groupId', name: 'CreateDraft', component: CreateDraftView, meta: { requiresAuth: true } },
  { path: '/groups/:groupId/edit', name: 'EditGroup', component: EditGroupView, meta: { requiresAuth: true } },
  { path: '/create-group', name: 'CreateGroup', component: CreateGroupView, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export async function authGuard(to, from, next) {
  const authStore = useAuthStore()
  const isAuthenticated = await authStore.checkAuth()
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next('/')
  } else {
    next()
  }
}

router.beforeEach(authGuard)

export default router
