#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
from fabric.api import *
from fabric.contrib.console import confirm

# Globals

env.project_name = 'findcontext'

# Environments

def dev():
    "Use the development webserver."
    env.hosts = ['findcontext.local']
    env.user = 'ryanshaw'
    env.path = '/Library/WebServer/Documents/%(project_name)s' % env
    env.vhosts_path = '/etc/apache2/sites'

def pro():
    "Use the production webserver."
    env.hosts = ['findcontext.org']
    env.user = 'ryanshaw'
    env.path = '/db/projects/%(project_name)s' % env
    env.vhosts_path = '/etc/httpd/sites.d/'

# Tasks

def test():
    "Run the test suite locally."
    for app in ['auth','contenttypes','sessions','sites','main','api']:
        env['app'] = app
        local("cd %(project_name)s; python manage.py test %(app)s" % env)
    
def test_remote():
    "Run the test suite remotely."
    require('hosts', provided_by=[dev])
    require('path')
    for app in ['auth','contenttypes','sessions','sites','main','api']:
        env['app'] = app
    run('cd %(path)s/releases/current/%(project_name)s;  ../../../bin/python manage.py test %(app)s' % env)
    
def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then
    run a full deployment.
    """
    require('hosts', provided_by=[dev])
    require('path')
    run('mkdir -p %(path)s' % env)
    with cd(env.path):
        run('virtualenv --no-site-packages .' % env)
        run('mkdir -p logs; mkdir -p releases; mkdir -p shared; mkdir -p packages' % env)
        run('cd releases; touch none; ln -sf none current; ln -sf none previous')
    deploy()
    
def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and then
    restart the webserver.
    """
    require('hosts', provided_by=[dev])
    require('path')
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    upload_tar_from_git()
    upload_local_settings()
    install_requirements()
    install_site()
    symlink_current_release()
    migrate()
    restart_webserver()
    sleep(2)
    local('open http://%(host)s/' % env)
    
def deploy_version(version):
    "Specify a specific version to be made live."
    require('hosts', provided_by=[dev])
    require('path')
    env.version = version
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous')
        run('ln -s %(version)s releases/current' % env)
    restart_webserver()
    
def rollback():
    """
    Limited rollback capability. Simple loads the previously current
    version of the code. Rolling back again will swap between the two.
    """
    require('hosts', provided_by=[dev])
    require('path')
    with cd(env.path):
        run('mv releases/current releases/_previous;')
        run('mv releases/previous releases/current;')
        run('mv releases/_previous releases/previous;')
    restart_webserver()

def clean():
    "Clean out old packages and releases."
    require('hosts', provided_by=[dev])
    require('path')
    if (confirm('Are you sure you want to delete everything on %(host)s?' % env, 
                default=False)):
        with cd(env.path):
            run('rm -rf packages; rm -rf releases')
    
# Helpers. These are called by other functions rather than directly.

def upload_tar_from_git():
    "Create an archive from the current Git master branch and upload it."
    require('release', provided_by=[deploy, setup])
    local('git archive --format=tar master | gzip > %(release)s.tar.gz' % env)
    run('mkdir -p %(path)s/releases/%(release)s' % env)
    put('%(release)s.tar.gz' % env, '%(path)s/packages/' % env)
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env)
    local('rm %(release)s.tar.gz' % env)

def upload_local_settings():
    "Upload the appropriate local settings file."
    require('release', provided_by=[deploy, setup])
    put('%(project_name)s/settings-%(host)s.py' % env, 
        '%(path)s/releases/%(release)s/%(project_name)s/settings_local.py' % env)

def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    run('cd %(path)s; pip install -E . -r ./releases/%(release)s/requirements.txt' % env)
    
def install_site():
    "Add the virtualhost file to apache."
    require('release', provided_by=[deploy, setup])
    sudo('cd %(path)s/releases/%(release)s; cp -f vhost-%(host)s.conf %(vhosts_path)s' % env, pty=True)
    
def symlink_current_release():
    "Symlink our current release."
    require('release', provided_by=[deploy, setup])
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous;')
        run('ln -s %(release)s releases/current' % env)
    
def migrate():
    "Update the database"
    require('hosts', provided_by=[dev])
    require('path')
    run('cd %(path)s/releases/current/%(project_name)s;  ../../../bin/python manage.py syncdb --noinput' % env)
    
def restart_webserver():
    "Restart the web server."
    sudo('apachectl restart', pty=True)
