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
import App from './App.vue'
import store from './store.js';
import router from './router'
import vuetify from './plugins/vuetify'

Vue.config.productionTip = false

import Amplify, { API, Auth } from 'aws-amplify'
// import Amplify, * as AmplifyModules from 'aws-amplify'
import { AWSIoTProvider } from '@aws-amplify/pubsub/lib/Providers';
import { AmplifyPlugin } from 'aws-amplify-vue'
import awsconfig from './aws-exports'

Amplify.configure(awsconfig)
API.configure(awsconfig)
Amplify.configure({
  ...awsconfig,
  API: {
    endpoints: [
      {
        name: "CDD_API",
        endpoint: awsconfig.cdd_api_endpoint,
        custom_header: async () => {
          // NOTE: The Id token is used instead of the access token since we cannot use CloudFormation
          // to add the resource server configuration and scopes directly. TODO: monitor CloudFormation
          // and CDK support to add
          return { Authorization: `Bearer ${(await Auth.currentSession()).getIdToken().getJwtToken()}` }
        }
      },
    ]
  }
})
Amplify.addPluggable(new AWSIoTProvider({
  aws_pubsub_region: awsconfig.aws_cognito_region,
  aws_pubsub_endpoint: 'wss://' + awsconfig.aws_iot_endpoint + '/mqtt',
}));

// Setup a separate Vue instance for messages
export const bus = new Vue();

Vue.use(AmplifyPlugin, API, Auth)
// It's important that you instantiate the Vue instance after calling Vue.use!
new Vue({
  store,
  router,
  vuetify,
  render: h => h(App)
}).$mount('#app')


