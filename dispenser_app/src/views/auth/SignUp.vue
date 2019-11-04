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
        <h1 class="display-1">Create account</h1>
      </v-card-title>
      <v-progress-linear v-if="isLoading" class="ma-0" :indeterminate="true" color="teal"></v-progress-linear>
      <v-card-text>
        <v-form>
          <v-text-field
            v-model="username"
            prepend-icon="mdi-account"
            name="username"
            label="Username"
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
          <v-text-field
            v-model="phoneNumber"
            prepend-icon="mdi-cellphone-arrow-down"
            name="phoneNumber"
            label="Phone number"
            type="text"
          ></v-text-field>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="success" @click="createAccount">Create Account</v-btn>
            <v-spacer></v-spacer>
          </v-card-actions>
        </v-form>
        <br />
        <p align="center" class="red--text">{{statusMessage}}</p>
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
      password: "",
      phoneNumber: "",
      showPassword: false,
      isLoading: false,
      statusMessage: ""
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
    async createAccount() {
      this.isLoading = true;
      Auth.signUp({
        username: this.username,
        password: this.password,
        attributes: {
          phone_number: this.phoneNumber
        },
        validationData: [] // optional
      })
        .then(data => {
          this.isLoading = false;
          console.log(data);
          this.$router.push({
            path: "/signUpConfirm",
            query: { username: this.username }
          });
        })
        .catch(err => {
          this.isLoading = false;
          this.statusMessage = err.message;
          console.log(err);
        });
    }
  }
};
</script>