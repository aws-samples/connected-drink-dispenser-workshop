/*
 * MIT No Attribution
 *
 * Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this
 * software and associated documentation files (the "Software"), to deal in the Software
 * without restriction, including without limitation the rights to use, copy, modify,
 * merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so.
*/
<template>
  <div class="home">
    <v-container class="grey lighten-5" v-if="pageState === 'completePage'" fluid>
      <v-row>
        <v-col cols="12" md="8">
          <Dispenser />
        </v-col>
        <v-col cols="6" md="4">
          <v-card outline tile>
            <!-- change to component -->
            <v-card-title>Leaderboard</v-card-title>
            <v-card-text>list</v-card-text>
            <v-card-text>stuff</v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <v-container v-else-if="pageState === 'loadingAssets'" fluid>
      <v-col cols="12">
        <v-row class="align-start justify-center">
          <v-card max-width="344px" outlined tile>
            <v-card-title class="justify-center">
              Loading Resources
            </v-card-title>
            <v-card-text v-if="!loadingText" class="justify-center">
              <p>
                Reading values from AWS Cloud
              </p>
            </v-card-text>
            <v-card-text v-else class="justify-center">
              <p>
                Reading values from AWS Cloud
              </p>
              <p class="red--text">This may take up to 30 seconds after account creation, please wait and <i>DO NOT</i> refresh or reload.
              </p>
            </v-card-text>
          </v-card>
        </v-row>
      </v-col>
    </v-container>
    <v-container v-else fluid>
      <v-col cols="12">
        <v-row class="align-start justify-end">
          <v-card max-width="344px" outlined tile>
            <v-card-title class="justify-end">
              Sign In!
              <v-icon>mdi-arrow-up-bold</v-icon>
            </v-card-title>
            <v-card-text>
              <p>
                Please sign in or
                <a href="/SignUp">create a new account</a>
              </p>
              <p>When logged in, your username will show and you be directed to the main dispenser view.</p>
            </v-card-text>
          </v-card>
        </v-row>
      </v-col>
      <v-col cols="12">
        <v-row class="align-center justify-center mx-auto">
          <v-card max-width="75%" outlined tile>
            <v-card-title>Welcome to the Connected Drink Dispenser Workshop!</v-card-title>
            <v-card-text>
              <p>
                This is the main web application you will use to complete the workshop. This home page will show cards for the different aspects of managing your drink dispenser. To start,
                <a
                  href="/SignUp"
                >create a new account</a> or
                <a href="/SignIn">sign in</a> (you can also sign in and out from the top right menu).
              </p>
              <p>All menu options are available above, but here are couple links to get started:</p>
              <ul>
                <li>
                  <a href="/docs/index.html" target="_blank">Documentation</a> - This will open the workshop documentation in a new window or tab. From there select the
                  <i>Workshop Participant</i> link.
                </li>
              </ul>
            </v-card-text>
          </v-card>
        </v-row>
      </v-col>
    </v-container>
  </div>
</template>

<script>
import Dispenser from "@/components/Dispenser";
import { Auth, API, PubSub } from "aws-amplify";
const sub1 = PubSub;

export default {
  name: "home",
  components: { Dispenser },
  data() {
    return {
      drawer: false,
      sub1: sub1,
      loadingText: false
    };
  },
  async created() {
    if (this.$store.getters.isAuth == true) {
      // If created with valid authentication, read in user assets,
      // read initial dispenser status then sub to MQTT topics
      let response;
      let authInfo;
      authInfo = await Auth.currentUserInfo();
      response = await API.post("CDD_API", "/getResources", {
        body: { cognitoIdentityId: authInfo.id }
      });
      console.log("resources response is ", response)
      // Get resources needed to complete setup
      await this.$store.dispatch("setAssets", response);
      // Read dispenser shadow and credit status, and set
      response = await API.get("CDD_API", "/status", {
        "queryStringParameters": {
          "dispenserId": this.$store.getters.dispenserId
        }
      });
      this.$store.dispatch("setStatus", response);
      console.log("/status response is ", response)
      console.log("before subscribe");
      this.sub1
        .subscribe("events/" + this.$store.getters.dispenserId)
        .subscribe({
          next: data => {
            console.log("Message received", data)
            console.log("loadingText is: ",this.loadingText)
          },
          error: error => console.error(error),
          close: () => console.log("Done")
        });
      console.log(
        "subscribed to topic: " + "events/" + this.$store.getters.dispenserId
      );
    }
  },
  mounted () {
    console.log("triggering loadingText going true")
    setTimeout(function () {
      this.loadingText = true;
    }.bind(this), 3000);
  },
  beforeDestroy() {
    // unsubscribe from "events/dispenserId"
    console.log("unsubscribing from events/nnn topic")
    this.sub1.unsubscribe()
  },
  computed: {
    isAuth() {
      if (this.$store.getters.isAuth == false) {
        return false;
      } else {
        return true;
      }
    },
    pageState() {
      if (this.$store.getters.isAuth == false) {
        // unauthed visit
        return "unAuth"
      } else {
        if (this.$store.getters.isAssets == false) {
          // loading or creating assets
          return "loadingAssets"
        } else {
          // authed used and resources have been loaded
          return "completePage"
        }
      }
    }
  }
};
</script>
