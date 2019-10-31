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
  <v-card outline tile>
    <v-list-item two-line>
      <v-list-item-content>
        <v-list-item-title class="headline">
          Dispenser:
          <b>{{ getDispenserId }}</b>
        </v-list-item-title>
        <v-list-item-subtitle>
          Credits: <span v-html="credits"></span>
        </v-list-item-subtitle>
      </v-list-item-content>
    </v-list-item>
    <v-card-text class="shrink">
      <v-btn outlined small color="primary" @click="expand = !expand">
        My Details
        <v-icon v-if="expand">mdi-menu-up-outline</v-icon>
        <v-icon v-else>mdi-menu-down-outline</v-icon>
      </v-btn>
      <v-expand-transition>
        <v-card-text v-show="expand">
          <v-row>
            <v-btn text>
              <a
                :download="certificateName + '-certificate.pem.crt'"
                :href="'data:octet/datastream;base64,' + certificatePemB64"
              >Certificate File</a>
            </v-btn>
            <v-btn text>
              <a
                :download="certificateName + '-private.pem.key'"
                :href="'data:octet/datastream;base64,' + privateKeyB64"
              >Private Key File</a>
            </v-btn>
            <v-btn text>
              <a
                download="AmazonRootCA1.pem"
                :href="'data:octet/datastream;base64,' + rootCAB64"
              >Amazon Root CA1 File</a>
            </v-btn>
          </v-row>
          <v-row>
            <v-card-text>
              <b>
                <u>AWS Console Details:</u>
              </b>
              <br />
              <b>Sign-in URL:</b> &nbsp;
              <a :href="getAccountUrl" target="_blank">{{getAccountUrl}}</a>
              <br />
              <b>Username:</b>
              &nbsp; {{getIamUsername}}
              <br />
              <b>Password:</b>
              &nbsp; {{getIamPassword}}
            </v-card-text>
          </v-row>
        </v-card-text>
      </v-expand-transition>
    </v-card-text>
    <v-card-text>My stuff</v-card-text>
  </v-card>
</template>

<script>
export default {
  name: "dispenser",
  data() {
    return {
      expand: false
    };
  },
  computed: {
    credits() {
      if (this.$store.getters.getCredits > 0) {
        return ('<span class="green--text">' + this.$store.getters.getCredits.toLocaleString("en-US", {
          style: "currency",
          currency: "USD"
        }) + '<span>');
      } else {
        return ('<span class="red--text">' + this.$store.getters.getCredits.toLocaleString("en-US", {
          style: "currency",
          currency: "USD"
        }) + '<span>');

      }
    },
    getDispenserId() {
      return this.$store.getters.dispenserId;
    },
    certificatePemB64() {
      if (this.$store.getters.certificatePem) {
        return btoa(this.$store.getters.certificatePem);
      } else {
        return "";
      }
    },
    privateKeyB64() {
      if (this.$store.getters.privateKey) {
        return btoa(this.$store.getters.privateKey);
      } else {
        return "";
      }
    },
    rootCAB64() {
      if (this.$store.getters.rootCA) {
        return btoa(this.$store.getters.rootCA);
      } else {
        return "";
      }
    },
    certificateName() {
      if (this.$store.getters.certificateName) {
        return this.$store.getters.certificateName;
      } else {
        return "";
      }
    },
    getAccountUrl() {
      if (this.$store.getters.getAccountUrl) {
        return this.$store.getters.getAccountUrl;
      } else {
        return "";
      }
    },
    getIamUsername() {
      if (this.$store.getters.getIamUsername) {
        return this.$store.getters.getIamUsername;
      } else {
        return "";
      }
    },
    getIamPassword() {
      if (this.$store.getters.getIamPassword) {
        return this.$store.getters.getIamPassword;
      } else {
        return "";
      }
    }
  }
};
</script>