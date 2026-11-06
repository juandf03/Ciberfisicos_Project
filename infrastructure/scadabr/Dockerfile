FROM tomcat:9.0-jre8-temurin
USER root
RUN apt-get update && apt-get install -y --no-install-recommends unzip && rm -rf /var/lib/apt/lists/*
RUN useradd --uid 10001 --create-home scada && mkdir -p /opt/scadabr-data && chown scada /opt/scadabr-data
COPY vendor/ScadaBR.war /tmp/ScadaBR.war
RUN mkdir -p /usr/local/tomcat/webapps/ScadaBR && cd /usr/local/tomcat/webapps/ScadaBR && \
    unzip -q /tmp/ScadaBR.war && rm /tmp/ScadaBR.war && \
    sed -i 's|^db.url=.*|db.url=/opt/scadabr-data/scadabrDB|' WEB-INF/classes/env.properties && \
    sed -i 's|^db.update.log.dir=.*|db.update.log.dir=/opt/scadabr-data|' WEB-INF/classes/env.properties && \
    grep -q '^db.url=/opt/scadabr-data/scadabrDB' WEB-INF/classes/env.properties && \
    chown -R scada:scada /usr/local/tomcat /opt/scadabr-data
ENV JAVA_OPTS="-Duser.home=/opt/scadabr-data -Dderby.system.home=/opt/scadabr-data -Dderby.stream.error.file=/opt/scadabr-data/derby.log"
USER 10001:10001
EXPOSE 8080
CMD ["catalina.sh", "run"]
