/*
 * MIT No Attribution
 *
 * Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this
 * software and associated documentation files (the "Software"), to deal in the Software
 * without restriction, including without limitation the rights to use, copy, modify,
 * merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so.
*/

import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import VueRouter from 'vue-router'
import store from './store'

import { Auth } from "aws-amplify";

Vue.use(Router)


const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import(/* webpackChunkName: "about" */ './views/About.vue'),
      meta: { requiresLogin: true }
    },
    {
      path: '/signUp',
      name: 'signUp',
      component: () => import(/* webpackChunkName: "signup" */ './views/auth/SignUp.vue')
    },
    {
      path: '/signUpConfirm',
      name: 'signUpConfirm',
      component: () => import(/* webpackChunkName: "confirm" */ './views/auth/SignUpConfirm.vue')
    },
    {
      path: '/forgotPassword',
      name: 'forgotPassword',
      component: () => import(/* webpackChunkName: "confirm" */ './views/auth/ForgotPassword.vue')
    },
    {
      path: '/passwordReset',
      name: 'passwordReset',
      component: () => import(/* webpackChunkName: "confirm" */ './views/auth/PasswordReset.vue')
    },
    {
      path: '/signIn',
      name: 'signIn',
      component: () => import(/* webpackChunkName: "signin" */ './views/auth/SignIn.vue')
    },
    {
      path: '/signOut',
      name: 'signOut',
      component: () => import(/* webpackChunkName: "signin" */ './views/auth/SignIn.vue')
    },
  ]
})
export default router;

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresLogin)) {
    Auth.currentAuthenticatedUser()
      .then(data => {
        console.log('beforeEach valid log in, to route is', to)
        store.dispatch('setLoggedIn', data)
        next()
      })
      .catch(err => {
        // Clear auth, just in case
        store.dispatch('setLoggedOut')
        console.log(err);
        // Pass path of next component
        console.log("next obj to: ", next)
        next({ path: "/signIn", query: {redirectTo: to.path }});
      });
  } else {
    Auth.currentAuthenticatedUser()
      .then(data => {
        store.dispatch('setLoggedIn', data)
        next()
      })
      .catch(err => {
        store.dispatch('setLoggedOut')
        console.log(err);
        next()
      });
  }
})