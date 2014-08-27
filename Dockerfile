FROM ianblenke/wildfly
MAINTAINER ian@blenke.com

# Expose the ports we're interested in
EXPOSE 8080

# This cluster is orchestrated using maestro-ng
USER root
RUN yum -y install python-pip yum-utils make automake gcc gcc-c++ kernel-devel git libaio
RUN yum-builddep -y python-pip
RUN pip install git+git://github.com/signalfuse/maestro-ng

RUN mkdir -p /opt/wildfly/jboss/standalone/data
RUN chown -R wildfly:wildfly /opt/wildfly/jboss/standalone/data

# Run everything below as the wildfly user
USER wildfly

WORKDIR /opt/wildfly

# Set the default command to run on boot
# This will boot wildfly in the standalone mode and bind to all interfaces
ADD standalone-ha-docker.xml /opt/wildfly/jboss/standalone/configuration/
ADD run.py /opt/wildfly/.docker/

VOLUME /opt/wildfly/jboss/standalone/data/
VOLUME /opt/wildfly/jboss/standalone/deployments/

CMD ["python", "/opt/wildfly/.docker/run.py"]
