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
    <v-card-title>
      Dispenser:
      <b>{{ getDispenserId }}</b>
    </v-card-title>
    <v-card-text class="shrink">
      <v-btn outlined small color="primary" @click="expand = !expand">My files
        <v-icon v-if="expand">mdi-menu-up-outline</v-icon>
        <v-icon v-else>mdi-menu-down-outline</v-icon>
      </v-btn>
      <v-expand-transition>
        <v-card-text v-show="expand">
          <v-btn text><a :download="certificateName + '-certificate.pem.crt'" :href="'data:octet/datastream;base64,' + certificatePemB64">Certificate File</a></v-btn>
          <v-btn text><a :download="certificateName + '-private.pem.key'" :href="'data:octet/datastream;base64,' + privateKeyB64">Private Key File</a></v-btn>
          <v-btn text><a download="AmazonRootCA1.pem" :href="'data:octet/datastream;base64,' + rootCAB64">Amazon Root CA1 File</a></v-btn>
          <v-btn text><a :href="getAccountUrl" target="_blank">Console Sign-in</a></v-btn>
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
      expand: false,
    };
  },
  computed: {
    isAuth() {
      if (this.$store.getters.isAuth == false) {
        return false;
      } else {
        return true;
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

    }

  }
};
</script>