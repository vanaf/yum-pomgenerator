#!/usr/bin/python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
import os
from yum.plugins import PluginYumExit, TYPE_INTERACTIVE
from yum import YumBase,YumAvailablePackage, misc
from urlparse import urlparse

requires_api_version = '2.1'
plugin_type = (TYPE_INTERACTIVE,)

def config_hook(conduit):
    parser = conduit.getOptParser()
    if hasattr(parser, 'plugin_option_group'):
        parser = parser.plugin_option_group

    parser.add_option('', '--generate-poms', dest='genpoms', action='store_true',
           default=False, help="generate poms")
    parser.add_option('', '--mvn-repo-id', dest='mvn_repo_id',
                      action='store', default=os.getenv('MVN_REPO_ID', 'remote-repository'),
                      help="Server Id to map on the <id> under <server> section of settings.xml In most cases, this parameter will be required for authentication")
    parser.add_option('', '--mvn-repo-url', dest='mvn_repo_url',
                      action='store', default=os.getenv('MVN_REPO_URL', 'please://specify.mvn.url/by/setting/MVN_REPO_URL'),
                      help="URL where the artifact will be deployed.")
    parser.add_option('', '--mvm-group-id-for-nonrepo-rpms', dest='mvn_gid_nonrepo',
                      action='store', default=os.getenv('MVN_GROUP_ID_FOR_NONREPO_RPMS', 'rpm'),
                      help="URL where the artifact will be deployed.")

def reqs2xml(package_reqs):
    if not package_reqs:
        return ''
    msg = '<dependencies>\n'
    for req in package_reqs:
        msg += '<dependency>\n'
        msg += pkg2xmlgav(req)
        msg += '\n<type>rpm</type>\n'
        msg += '<classifier>{}</classifier>\n'.format(req.arch)
        msg += '</dependency>\n'
    msg += '</dependencies>'
    return msg

def pkg2xmlgav(package, group_id=None):
    repo = package.repo
    try:
        repo_url = repo.metalink if repo.metalink else repo.mirrorlist if repo.mirrorlist else repo.baseurl[0]
        host = urlparse(repo_url).netloc.split(':')[0]
        group_id = '{}.rpm'.format('.'.join([ x for x in list(reversed(host.split('.'))) if not 'mirror' in x ]))
    except AttributeError:
        print "## Cannot detect group_id for {}, using group_id={}".format(package, group_id)
    
    return """  <groupId>{group_id}</groupId>
  <artifactId>{artifact_id}</artifactId>
  <version>{version}</version>""".format(group_id=group_id, artifact_id=package.name,version=package.vr)

def postresolve_hook(conduit):
    opts, commands = conduit.getCmdLine()
    if opts.genpoms:
        ti = conduit.getTsInfo()
        packages_reqs = {}
        for tm in ti.getMembers():
            if not tm.po in packages_reqs:
                packages_reqs[tm.po] = set()
            for parent in tm.depends_on:
                if not parent in packages_reqs:
                    packages_reqs[parent] = set()
                packages_reqs[parent].add(tm.po)
        print '==== MVN DEPLOY COMMANDS ===='
        for package in packages_reqs:
            msg = """<project>
  <modelVersion>4.0.0</modelVersion>
  {gav}
  <packaging>rpm</packaging>
  <description>{description}</description>
{dependencies}
</project>""".format(gav=pkg2xmlgav(package, opts.mvn_gid_nonrepo), description=misc.to_xml(package.description), dependencies=reqs2xml(packages_reqs[package]))
            rpmPath = package.localPkg()
            pomPath = '{}.pom'.format(rpmPath)
            f = open(pomPath, 'w')
            f.write(msg)
            f.close()
            print "mvn deploy:deploy-file -Dfile='{rpm_filename}' -DpomFile='{pom_filename}' -Dclassifier='{classifier}' -Durl='{url}' -DrepositoryId='{repo_id}'".format(rpm_filename=os.path.basename(rpmPath), pom_filename=os.path.basename(pomPath), classifier=package.arch, url=opts.mvn_repo_url, repo_id=opts.mvn_repo_id)
        print '==== END OF MVN DEPLOY COMMANDS ===='
