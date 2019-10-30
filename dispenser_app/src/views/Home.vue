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
    <v-container class="grey lighten-5" v-if="isAuth" fluid>
      <v-row>
        <v-col cols="12" md="8">
          <Dispenser />
        </v-col>
        <v-col cols="6" md="4">
          <v-card outline tile>
            <!-- change to component -->
            <v-card-title>Leaderboard</v-card-title>
            <v-card-text>list</v-card-text>
          </v-card>
        </v-col>
      </v-row>
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
import { PubSub } from "aws-amplify";
const sub1 = PubSub;

export default {
  name: "home",
  components: { Dispenser },
  props: ['userPW'],
  data() {
    return {
      drawer: false,
      sub1: sub1
    };
  },
  created() {
    // If created with valid authentication, read in user assets,
    // read initial dispenser status then sub to MQTT topics
    //
    console.log("/Home route is", this.$route)
    if (this.$store.getters.isAuth == true) {
      console.log("did we get the value: " + this.$props.userPW)
      // Load user assets and set vuex
      // API.post("CDD_API", "/getResources", {
      //   body: { password: this.password, cognitoIdentityId: info.id }
      // })
      //   .then(response => {
      //     this.isLoading = false;
      //     this.statusMessage = "";
      //     this.$store.dispatch("setAssets", response);
      //     // // With resources loaded (iot policy applied), subscribe
      //     // PubSub.subscribe('events/' + this.$store.getters.dispenserId).subscribe({
      //     //   next: data => console.log('Message received', data),
      //     //   error: error => console.error(error),
      //     //   close: () => console.log('Done'),
      //     // });

      //   })
      //   .catch(error => {
      //     this.statusMessage = "Error loading or creating resources";
      //     this.isLoading = false;
      //     console.log("err", error);
      //   });

      // Subscribe to the MQTT topics
      // With resources loaded (iot policy applied), subscribe
      this.sub1.subscribe("events/" + this.$store.getters.userName).subscribe({
        next: data => console.log("Message received", data),
        error: error => console.error(error),
        close: () => console.log("Done")
      });
      console.log("got to subscribe stuff");
    }
  },
  computed: {
    isAuth() {
      if (this.$store.getters.isAuth == false) {
        return false;
      } else {
        // Subscribe to the MQTT topics
        // With resources loaded (iot policy applied), subscribe
        sub1.subscribe("events/" + this.$store.getters.dispenserId).subscribe({
          next: data => console.log("Message received", data),
          error: error => console.error(error),
          close: () => console.log("Done")
        });
        console.log(
          "subscribed to topic: " + "events/" + this.$store.getters.dispenserId
        );
        return true;
      }
    }
  }
};
</script>
