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
        <h1 class="display-1">Choose new password</h1>
      </v-card-title>
      <v-progress-linear v-if="isLoading" class="ma-0" :indeterminate="true" color="teal"></v-progress-linear>
      <v-card-text>
        <v-form>
          <v-text-field v-model="username" prepend-icon="mdi-account" name="username" :label="username" type="text"></v-text-field>
          <v-text-field
            v-model="confirmCode"
            prepend-icon="mdi-lock"
            name="confirmationCode"
            label="Confirmation code"
            type="text"
          ></v-text-field>
          <v-text-field
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            prepend-icon="mdi-lock"
            id="password"
            name="password"
            label="Password"
            :append-icon="showPassword ? 'mdi-eye' :
            'mdi-eye-off'"
            @click:append="showPassword = 
            !showPassword"
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
  // TODO: Fix reset - username not being taken
  name: "SignUp",
  data() {
    return {
      username: "",
      confirmCode: "",
      password: "",
      showPassword: false,
      isLoading: false
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
    async resetPassword() {
      this.isLoading = true;
      // Collect confirmation code and new password , then
      Auth.forgotPasswordSubmit(this.username, this.confirmCode, this.password)
        .then(data => {
          this.isLoading = false;
          console.log(data);
        })
        .catch(err => {
          this.isLoading = false;
          console.log(err);
        });
    }
  }
};
</script>