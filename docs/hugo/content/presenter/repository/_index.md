---
license: MIT-0
copyright: Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
chapter: false
pre: <i class="fas fa-greater-than"></i>&nbsp;
next: 
prev: 
title: Repository Layout
weight: 50
---

## Repository Layout

An understanding of the repository is not required to run the workshop, but can be helpful when deploying the cloud assets or to understand supporting resources. The [Connected Drink Dispenser Repository](https://github.com/aws-samples/connected-drink-dispenser-workshop) directory structure looks similar to this:

```text
├── deploy                  <--- Build and deploy the CloudFormation stack
├── dispenser_app           <--- Single Page App (SPA)
├── docs                    <--- Participant and presenter docs
...
└── README.md                <--- Main GitHub documentation page
```

The main directories of interest are:

- `deploy` - Creates and optionally deploys all assets to the cloud for the workshop.
- `dispenser_app` - The SPA for managing per-workshop resources (admin user) and the web app for participants to interact with the device.
- `docs` - The source files to create the documentation site for inclusion into the main web site along side the dispenser app. *You are current here!*
