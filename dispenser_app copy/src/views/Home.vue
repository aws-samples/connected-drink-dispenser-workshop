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
              New User?
              <v-icon>mdi-arrow-up-bold</v-icon>
            </v-card-title>
            <v-card-text>
              <p>
                Please sign in or
                <a href="/SignUp">create a new account</a>
              </p>
              <p>When logged in, your username will show, and you can view your unique details by clicking your name.</p>
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
import Dispenser from '@/components/Dispenser'
export default {
  name: "home",
  components: { Dispenser },
data() {
    return {
      drawer: false
    };
  },
  computed: {
    isAuth() {
      if (this.$store.getters.isAuth == false) {
        return false;
      } else {
        return true;
      }
    }
  }
};
</script>
