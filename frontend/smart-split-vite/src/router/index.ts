import { createRouter, createWebHistory } from 'vue-router';
import Home from '../pages/Home.vue';
import Groups from '../pages/Groups.vue';
import GroupDetails from '../pages/GroupDetails.vue';
import Add from '../pages/Add.vue';
import Activity from '../pages/Activity.vue';
import Profile from '../pages/Profile.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/groups',
    name: 'Groups',
    component: Groups
  },
  {
    path: '/groups/:id',
    name: 'GroupDetails',
    component: GroupDetails,
    props: true
  },
  {
    path: '/add',
    name: 'Add',
    component: Add
  },
  {
    path: '/activity',
    name: 'Activity',
    component: Activity
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
