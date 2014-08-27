#!/usr/bin/env python

# Start script for a JBOSS cluster node.

import logging
import os
import sys
import re

from maestro.guestutils import *

# Setup logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

os.chdir(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..'))

GOSSIPROUTER_LIST = ','.join(["%s[%s]" % tuple(host_port.split(':')) for host_port in get_node_list('gossiprouter', ports=['gossiprouter'])])
GOSSIPROUTER_COUNT = len(get_node_list('gossiprouter', ports=['gossiprouter']))

# Setup the various JVM options.
jvm_opts = [
    '-server',
    '-showversion',
    '-Dvisualvm.display.name="{}/{}"'.format(
        get_environment_name(), get_container_name()),
]

# Add any auto-discovered details from maestro-ng
jvm_opts += [
    '-Djboss.node.name={}'.format(get_container_name()),
    '-Ddocker.gossiprouter.hosts={}'.format(GOSSIPROUTER_LIST),
    '-Ddocker.gossiprouter.count={}'.format(GOSSIPROUTER_COUNT),
    '-Djava.library.path=/lib64:/opt/wildfly/jboss/modules/system/layers/base/org/hornetq/main/lib/linux-x86_64'
]

# Process the standalone-ha-docker.xml file
fp = open('/opt/wildfly/jboss/standalone/configuration/standalone-ha-docker.xml','r')
# Finding all occurrences of ${jboss.variable:default}
expr = re.compile("\$\{([^\}:]+)\:?([^\}]*)\}?", re.M)
lines = fp.read()
fp.close()
for el in expr.findall(lines):
  # Pull out the jboss.variable
  jboss_variable = el[0]
  # Pull out the default
  default = el[1]
  # Convert jboss.variable to JBOSS_VARIABLE
  env_variable = re.sub(r"\.", "_", jboss_variable).upper()
  # Check if there is an environment variable named JBOSS_VARIABLE
  if env_variable in os.environ:
    # Add the -D define for the jboss.variable if a value was found in the environment
    value = os.environ.get(env_variable)
    jvm_opts += [ "-D{}='{}'".format( jboss_variable, value ) ]

os.environ['JAVA_OPTS'] = ' '.join(jvm_opts) + os.environ.get('JVM_OPTS', '')

with open("/opt/wildfly/jboss/bin/standalone.conf", "a") as conffile:
      conffile.write("JAVA_OPTS=$JAVA_OPTS\ '{}'".format(os.environ['JAVA_OPTS']))

os.makedirs('/opt/wildfly/jboss/standalone/data/content')
os.makedirs('/opt/wildfly/jboss/standalone/data/tx-object-store/ShadowNoFileLockStore/defaultStore')

os.execl('/opt/wildfly/jboss/bin/standalone.sh','--server-config=/opt/wildfly/jboss/standalone/configuration/standalone-ha-docker.xml')
