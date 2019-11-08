FROM ubuntu:18.04

# Run command to build new local image
# docker build -t gadams999/hugo-ubuntu:0.59.1 .
ARG HUGO_VERSION=0.59.0

# docker build -t gavinaws/hugo54.0-ubuntu .
# ARG HUGO_VERSION=0.54.0

ENV DOCUMENT_DIR=/hugo-project

# python-minimal for pygments support for asciidoctor
RUN apt-get update && apt-get upgrade -y \
      && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
           curl ruby ruby-dev make cmake build-essential bison flex graphviz \
           openjdk-11-jre python \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/* \
      && rm -rf /tmp/*

RUN mkdir -p /opt/plantuml && cd /opt/plantuml \
      && UML=http://sourceforge.net/projects/plantuml/files/plantuml.jar/download \
      && curl -JLO ${UML}
COPY plantuml /usr/local/bin/plantuml
RUN chmod a+x /usr/local/bin/plantuml
RUN gem install --no-document asciidoctor asciidoctor-revealjs asciidoctor-html5s \
         rouge asciidoctor-confluence asciidoctor-diagram coderay pygments.rb

ADD https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${HUGO_VERSION}_Linux-64bit.tar.gz /tmp/hugo.tgz

RUN cd /usr/local/bin && tar -xzf /tmp/hugo.tgz && rm /tmp/hugo.tgz

RUN mkdir ${DOCUMENT_DIR}
WORKDIR ${DOCUMENT_DIR}

VOLUME ${DOCUMENT_DIR}
ENV CLASSPATH=/opt/plantuml
ENV PATH=${DOCUMENT_DIR}:$PATH
CMD ["hugo","server","--bind","0.0.0.0"]


