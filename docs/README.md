# Connected Drink Dispenser Documentation

## Overview

The Connected Drink Dispenser (CDD) documentation is statically generated from Hugo and made available
to participants from the main website domain name (/docs). This is done locally, and then the generated output is synched to the S3 bucket. The CloudFront deployment then serves the content up in the same context as the dispenser app.

## Building and deploying documentation

There are some prerequisites to build the documentation and sync to S3:

* AWS CLI - Configured with permissions to update the target S3 bucket.
* [htmltest](https://github.com/wjdp/htmltest) - A local HTML test tool to verify generated site content. Executable must be on the PATH (can run `htmltest` from any directory on the command line/terminal).
* [Docker Desktop](https://www.docker.com/products/docker-desktop) - Ability to run Docker containers locally.
* S3 Bucket Name - The name of the S3 bucket serving as the CloudFront origin to CloudFormation. **Note:** This is not necessarily the same as the domain name given.
* Linux or macOS environment - The `make_hugo.sh` script automates the steps to build, test, and deploy the documentation. At this point there is no corresponding PowerShell script to do the same for Windows.

**To build the content:**

1. Launch a terminal and change to the `docs/` folder
1. In `hugo/config.toml`, change the `baseURL` to be the *base* domain name of your CloudFront Distribution, with HTTPS. For example, `"https://cdd.example.com"`.
1. Run `./make_hugo.sh` which will create and test HTML content

That's it. The content for upload now resides in the `docs/hugo/public` folder. You can test locally on your system by opening the `index.html` file. A couple links (the logo and local content in the *More* section) will link to the content of the `baseURL` you modified above.

**To build *and* test locally:**

To test while making and saving changes, follow the first two steps above, and then run in *develop* mode:

```bash
$ ./make_hugo.sh --develop
Building sites ...
...
Serving pages from memory
Running in Fast Render Mode. For full rebuilds on change: hugo server --disableFastRender
Web Server is available at http://localhost:1313/ (bind address 0.0.0.0)
Press Ctrl+C to stop
```

This will do a full build of the content, test the HTML links, and then launch a local web server. Open a browser to http://localhost:1313 and any changes and file save to source content will be reflected immediately in the browser. In this mode, any diagrams created by Asciidoc or PlantUML will show as broken links. To verify those, complete build and then open via the file system like in the steps above.

**To build *and* sync content:**

Follow the first two steps above. For the `make_hugo.sh` command add the `--sync` flag and the S3 bucket where content should be copied:

```bash
$ ./make_hugo.sh --sync cdd.example.com/docs
Building sites ...
...
upload: hugo/public/index.html to s3://bucket_name/docs/index.html
...
```

That will build, test, and then remove any existing content and copy over the newly created content.
