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
<template>
  <v-app-bar app color="primary" dark>
    <v-toolbar-title>Connected Drink Dispenser</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn text rounded href="/docs/index.html" target="_blank">Documentation</v-btn>
    <div v-if="userName">
      <!-- <v-btn text rounded @click="signOut"> -->
      <v-btn text rounded>
        <!-- TODO Add modal with user details formatted from vuex -->
        {{userName}}
      </v-btn>
      <v-btn text rounded @click="signOut">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </div>
    <div v-else>
      <v-btn text rounded href="/signIn">Sign In</v-btn>
      </div>
  </v-app-bar>
</template>

<script>
import { Auth } from "aws-amplify";

export default {
  name: "Navbar",
  data() {
    return {
      drawer: false
    };
  },
  computed: {
    userName() {
      if (this.$store.getters.userName == false) {
        return false;
      } else {
        return this.$store.getters.userName;
      }
    }
  },
  methods: {
    signOut() {
      
      Auth.signOut()
        .then(data => {
          console.log(data);
          this.$store.dispatch("setLoggedOut")
          this.$router.go();
        })
        .catch(err => {
          console.log(err);
          this.$router.push({
            path: "/"
          });
        });
    }
  }
};
</script>