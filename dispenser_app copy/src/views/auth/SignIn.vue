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
  <v-card width="400" class="mx-auto mt-5">
    <v-card-title darkcolor="primary">
      <h1 class="display-1">Sign in</h1>
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
        <p align="right">
          <a href="/forgotPassword">Forgot password</a>
        </p>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <!-- stopProp to remove errors for password managers -->
          <v-btn
            color="success"
            @click="loginUser"
            v-on:keydown.enter="$event.stopPropagation()"
          >Sign In</v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-form>
      <br />
      <p align="center" class="red--text">{{statusMessage}}</p>
      <p align="center">
        Create an account?
        <a href="signUp">Sign up</a>
      </p>
    </v-card-text>
  </v-card>
</template>

<script>
import { Auth, API } from "aws-amplify";
//import { AmplifyEventBus } from "aws-amplify-vue";

export default {
  name: "SignUp",
  data() {
    return {
      username: this.$route.query.username,
      password: "",
      showPassword: false,
      isLoading: false,
      redirectTo: this.$route.query.redirectTo,
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
    loginUser() {
      this.isLoading = true;
      console.log("signing in user from", this.$route);
      Auth.signIn(this.username, this.password)
        .then(user => {
          console.log(user);
          Auth.currentUserInfo()
            .then(info => {
              this.$store.dispatch("setLoggedIn", user);
              this.statusMessage =
                "Loading or creating resources, please wait, may take 30 seconds on first login";
              console.log("user_info is ", info);
              API.post("CDD_API", "/getResources", {
                body: { password: this.password , cognitoIdentityId: info.id}
              })
                .then(response => {
                  this.isLoading = false;
                  this.statusMessage = "";
                  this.$store.dispatch("setAssets", response);
                  if (!this.redirectTo) {
                    // No called route, send to root (/)
                    this.$router.push({
                      path: "/"
                    });
                  } else {
                    // When authenticated, forward to auth required route
                    this.$router.push({
                      path: this.redirectTo
                    });
                  }
                })
                .catch(error => {
                  this.statusMessage = "Error loading or creating resources";
                  this.isLoading = false;
                  console.log("err", error);
                });

              console.log("current user info ", info);
            })
            .catch(error => {
              console.log(error);
            });
        })
        .catch(err => {
          // auth failed, display error and try again
          this.isLoading = false;
          this.statusMessage = err.message;
          console.log(err);
        });
    }
  }
};
</script>