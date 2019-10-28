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
  <v-flex>
    <v-card width="400" class="mx-auto mt-5">
      <v-card-title dark color="primary">
        <h1 class="display-1">Forgot your password?</h1>
      </v-card-title>
      <v-progress-linear v-if="apiRequest" class="ma-0" :indeterminate="true" color="teal"></v-progress-linear>
      <v-card-text>
        <v-form>
          <p>Please enter your email address</p>
          <v-text-field
            v-model="username"
            prepend-icon="mdi-account"
            name="username"
            label="user name"
            type="text"
          ></v-text-field>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="success" @click="resetPassword">Reset Password</v-btn>
            <v-spacer></v-spacer>
          </v-card-actions>
        </v-form>
        <br />
        <p align="center">
          Have an account?
          <a href="signIn">Sign in</a>
        </p>
      </v-card-text>
    </v-card>
  </v-flex>
</template>



<script>
import { Auth } from "aws-amplify";
// import { AmplifyEventBus } from "aws-amplify-vue";

export default {
  name: "SignUp",
  data() {
    return {
      username: "",
      showPassword: false,
      apiRequest: false
    };
  },
  methods: {
    async isUserSignedIn() {
      try {
        const userObj = await Auth.currentAuthenticatedUser();
        this.signedIn = true;
        console.log(userObj);
      } catch (err) {
        this.signedIn = false;
        console.log(err);
      }
    },
    resetPassword() {
      this.apiRequest = true;
      Auth.forgotPassword(this.username)
        .then(data => {
          console.log(data);
          this.$router.push({
            path: "passwordReset",
            query: { email: this.username }
          });
        })
        .catch(err => console.log(err));
    }
  }
};
</script>