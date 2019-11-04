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

import Vuex from 'vuex';
import Vue from 'vue';
// import createPersistedState from 'vuex-persistedstate';

Vue.use(Vuex);

const store = new Vuex.Store({
  // plugins: [createPersistedState()],
  state: {
    username: "",
    signedIn: false,
    dispenserId: "",
    certificateName: "",
    certificateArn: "",
    certificatePem: "",
    privateKey: "",
    rootCA: "",
    accountUrl: "",
    iamUsername: "",
    iamPassword: "",
    ledStatus: {
      state: "",
      color: "",
      text: ""
    },
    ringLedStatus: {
      count: 0,
      color: ""
    },
    credits: 0,
  },

  getters: {
    userName: state => {
      if (state.signedIn) {
        return state.username
      } else {
        return false
      }
    },
    isAuth: state => {
      if (state.signedIn) {
        return true
      } else {
        return false
      }
    },
    isAssets: state => {
      if (state.dispenserId === "") {
        return false
      } else {
        return true
      }
    },
    dispenserId: state => {
      if (state.dispenserId == null) {
        return false
      } else {
        return state.dispenserId
      }
    },
    certificateName: state => {
      if (state.certificateName == null) {
        return false
      } else {
        return state.certificateName
      }
    },
    certificateArn: state => {
      if (state.certificateArn == null) {
        return false
      } else {
        return state.certificateArn
      }
    },
    certificatePem: state => {
      if (state.certificatePem == null) {
        return false
      } else {
        return state.certificatePem
      }
    },
    privateKey: state => {
      if (state.privateKey == null) {
        return false
      } else {
        return state.privateKey
      }
    },
    rootCA: state => {
      if (state.rootCA == null) {
        return false
      } else {
        return state.rootCA
      }
    },
    getAccountUrl: state => {
      if (state.accountUrl == null) {
        return false
      } else {
        return state.accountUrl
      }
    },
    getIamUsername: state => {
      if (state.iamUsername == null) {
        return false
      } else {
        return state.iamUsername
      }
    },
    getIamPassword: state => {
      if (state.iamPassword == null) {
        return false
      } else {
        return state.iamPassword
      }
    },
    getCredits: state => {
      return state.credits
    },
    getLedStatus: state => {
      return state.ledStatus.state
    },
    getLedColor: state => {
      return state.ledStatus.color
    },
    getLedText: state => {
      return state.ledStatus.text
    },
    getRingLed: state => {
      return state.ringLedStatus
    }
  },

  mutations: {
    loggedIn(state, payload) {
      state.username = payload.username;
      state.jwt = payload.jwt;
      state.signedIn = true;
      console.log('logged in set');
    },
    loggedOut(state) {
      if (state) {
        state.username = "";
        state.signedIn = false;
        state.dispenserId = "";
        state.certificateName = "";
        state.certificateArn = "";
        state.certificatePem = "";
        state.privateKey = "";
        state.rootCA = "";
        state.accountUrl = "";
        state.iamUsername = "";
        state.iamPassword = "";
        state.ledStatus = {
          color: "",
          state: "",
          text: ""
        },
        state.ringLedStatus = {
          count: 0,
          color: ""
        },
        state.credits = 0
      }
      console.log('logged OUT set');
    },
    updateAssets(state, assetObj) {
      console.log("in updateAssets mutation")
      state.dispenserId = assetObj.dispenserId;
      state.certificateArn = assetObj.assets.iot.certificateArn;
      state.certificateName = assetObj.assets.iot.certificateArn.split("/").pop().substring(0, 10);
      state.certificatePem = assetObj.assets.iot.certificatePem;
      state.privateKey = assetObj.assets.iot.privateKey;
      state.rootCA = assetObj.assets.iot.rootCA;
      // Set the sign-in link as the account number is in the arn
      state.accountUrl = `https://${state.certificateArn.split(":")[4]}.signin.aws.amazon.com/console/`
      state.iamUsername = assetObj.assets.iam_user.username;
      state.iamPassword = assetObj.assets.iam_user.password;
    },
    updateStatus(state, statusObj) {
      console.log("in updateStatus mutation")
      state.credits = statusObj.credits;
      state.ringLedStatus.count = statusObj.led_ring_state.count;
      state.ringLedStatus.color = statusObj.led_ring_state.color;
      // Set LED values to be easily read from components
      state.ledStatus.state = statusObj.led_state;
      if (statusObj.led_state === "on") {
        state.ledStatus.color = "red";
        state.ledStatus.text = "ON"
       } else {
        state.ledStatus.color = "grey";
        state.ledStatus.text = "OFF"
       }
    }
  },

  actions: {
    setLoggedIn(context, payload ) {
      context.commit('loggedIn', payload )
    },
    setLoggedOut(context) {
      context.commit('loggedOut')
    },
    setAssets(context, assetObj) {
      // body response from call to /getResources API
      context.commit('updateAssets', assetObj);
    },
    setStatus(context, statusObj) {
      // body response from call to /status API
      context.commit('updateStatus', statusObj);
    }
  }
});

export default store;
