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
          Credits:
          <span v-html="creditText"></span>
        </v-list-item-subtitle>
      </v-list-item-content>
    
    </v-list-item>
    <v-card-text>
      <v-btn v-if="credits >= 1" @click="requestDispense">Dispense!</v-btn>
      <v-btn v-else>Sad Panda {{credits}}</v-btn>
    </v-card-text>
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
            <v-card-text>
              <b>
                <u>AWS IoT Details:</u>
              </b>
              <br />
              <b>Endpoint:</b>
              &nbsp; {{this.iotEndpoint}}
            </v-card-text>

          </v-row>
        </v-card-text>
      </v-expand-transition>
    </v-card-text>
    <v-container class="grey lighten-5" fluid>
      <v-row>
        <v-col>
          <v-card outline tile>
            <v-list-item three-line>
              <v-list-item-content>
                <div class="overline mb-4">CURRENT CARRIER BOARD LED STATUS</div>
                <v-list-item-title class="headline mb-1">LED</v-list-item-title>
                <v-list-item-subtitle>Use the buttons below to change the LED state</v-list-item-subtitle>
              </v-list-item-content>
              <v-avatar v-bind:color="ledColor" size="36">
                <span class="white--text">{{ledText}}</span>
              </v-avatar>
            </v-list-item>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn v-on:click="setLed('on')" class="ma-2" outlined>
                <v-icon>mdi-lightbulb</v-icon>
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn v-on:click="setLed('off')" class="ma-2" outlined>
                <v-icon>mdi-lightbulb-off</v-icon>
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn v-on:click="setLed('toggle')" class="ma-2" outlined>
                <v-icon>mdi-light-switch</v-icon>
              </v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-col>

        <v-col>
          <v-card outline tile height="100%">
            <v-list-item three-line>
              <v-list-item-content>
                <div class="overline mb-4">CREDIT INDICATOR</div>
                <v-list-item-title class="headline mb-1">Ring LED</v-list-item-title>
                <v-list-item-subtitle>Zero to three red LEDS indicate less than $1.00, all five show credits available for dispense</v-list-item-subtitle>
              </v-list-item-content>
              <v-avatar
                v-for="n in ringLed.count"
                v-bind:key="n"
                v-bind:color="ringLed.color"
                size="36"
              ></v-avatar>
            </v-list-item>
            <v-card-actions>Zero to three red LEDS indicate less than $1.00, all five show credits available for dispense</v-card-actions>
          </v-card>
        </v-col>
      </v-row>
      <v-expansion-panels>
        <v-expansion-panel>
          <v-expansion-panel-header disable-icon-rotate>
            Share the Love
            <template v-slot:actions>
              <v-icon color="red">mdi-hand-heart</v-icon>
            </template>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            Select the dispenser that you wish to give credit. You cannot give yourself credits, and there is a five second delay in giving credits to others.
            <v-col>
              <v-text-field
                label="Enter another's Dispenser ID to give credits"
                v-model.trim="targetDispenser"
                type="number"
              >
                <template v-slot:append>
                  <v-btn
                    v-if="(targetDispenser >= 100) && (targetDispenser != getDispenserId) && (shareGuardPassed)"
                    tile
                    class="ma-0"
                    v-on:click="dispenseDrinkCredits(targetDispenser)"
                  >Send Credit!</v-btn>
                  <v-btn v-else disabled :pressed="false" tile class="ma-0"></v-btn>
                </template>
              </v-text-field>
              <b>Last credit response message:</b>
              {{lastCreditMessage}}
            </v-col>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-container>
  </v-card>
</template>

<script>
import { API } from "aws-amplify";
import awsmobile from '../aws-exports.js';

export default {
  name: "dispenser",
  data() {
    return {
      expand: false,
      lastCreditMessage: "Haven't given credits yet",
      targetDispenser: null,
      shareGuardPassed: true,
      iotEndpoint: awsmobile.aws_iot_endpoint
    };
  },
  methods: {
    setLed: function(state) {
      API.get("CDD_API", "/command", {
        queryStringParameters: {
          setLed: state
        }
      });
    },
    dispenseDrinkCredits: function(targetDispenser) {
      API.get("CDD_API", "/credit", {
        queryStringParameters: {
          dispenserId: targetDispenser
        },
        responseType: "text"
      })
        .then(response => {
          this.lastCreditMessage = response;
          this.targetDispenser = null;
          this.shareGuardPassed = false;
          this.shareGuardTimer = setTimeout(this.clearGuard, 5000);
        })
        .catch(error => {
          console.log(error);
        });
    },
    clearGuard: function() {
      this.shareGuardPassed = true;
    },
    requestDispense: function() {
      API.get("CDD_API", "/dispense", {
        queryStringParameters: {
          dispenserId: this.getDispenserId
        }
      });
    }
  },
  computed: {
    credits() {
      return this.$store.getters.getCredits
    },
    creditText() {
      if (this.$store.getters.getCredits > 0) {
        return (
          '<span class="green--text">' +
          this.$store.getters.getCredits.toLocaleString("en-US", {
            style: "currency",
            currency: "USD"
          }) +
          "<span>"
        );
      } else {
        return (
          '<span class="red--text">' +
          this.$store.getters.getCredits.toLocaleString("en-US", {
            style: "currency",
            currency: "USD"
          }) +
          "<span>"
        );
      }
    },
    dispenseButtonState() {
      if (
        this.targetDispenser >= 100 &&
        this.targetDispenser != this.getDispenserId
      ) {
        return null;
      } else {
        return false;
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
    },
    ledColor() {
      return this.$store.getters.getLedColor;
    },
    ledText() {
      return this.$store.getters.getLedText;
    },
    ringLed() {
      return this.$store.getters.getRingLed;
    },
    dispenseStatus() {
      if (this.$store.getters.getCredits >= 1) {
        return "green"
      } else {
        return "red"
      }
    }
  }
};
</script>