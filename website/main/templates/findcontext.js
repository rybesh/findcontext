/*jslint eqeqeq: true, immed: true, newcap: true, nomen: true, onevar: true, passfail: true, plusplus: true, regexp: true, undef: true, white: true, indent: 2*/
/*global jetpack, console, escape, $ */

jetpack.future.import('menu');
jetpack.future.import('selection');
jetpack.future.import("slideBar");

var BASE_URI = 'http://{{ request.get_host }}/'
var SIDEBAR_URI = BASE_URI + 'sidebar/';
var API_URI = BASE_URI + 'api/';
var USER = '{{ user.username }}';
var PASS = 'celt138';

var pkg = null;
var slidebar = null;

function base64encode(string) {
  return jetpack.tabs.focused.contentWindow.btoa(string);
}

function log(message) {
  $.ajax({
    'type': 'POST',
    'url': API_URI + 'log/',
    'contentType': 'text/plain',
    'data': message,
    'processData': false,
    'beforeSend': function(request) {
      request.setRequestHeader(
        'Authorization', 
        'Basic ' + base64encode(USER + ':' + PASS));
    }
  });
  console.log(message);
}

function initPackage(callback) {
  if (pkg) {
    callback(pkg);
  } else {
    $.getJSON(API_URI + 'package/', function (packages) {
      pkg = packages[0]; // TODO: allow user to select
      callback(pkg);
    });
  }
}

function updateSlidebar(callback) {
  var content = (SIDEBAR_URI + '?p=' + pkg.uri + '&q=' + escape(jetpack.selection.text));
  if (slidebar) {
    slidebar.iframe.addEventListener(
      "DOMContentLoaded", function iframeLoaded() {
        slidebar.iframe.removeEventListener("DOMContentLoaded", iframeLoaded, false);
        callback(slidebar);
      }, false);
    slidebar.contentDocument.location = content;
  } else {
    jetpack.slideBar.append({
      url: content,
      width: 250,
      persist: true,
      onReady: function (slbr) {
        slidebar = slbr;
        callback(slidebar);
      }
    });
  }
}

function addSlidebarEventListener(slidebar) {
  var root, node, url;
  root = slidebar.contentDocument.rootElement;
  root.addEventListener('mousedown', function (event) {
    node = event.target;
    while (node !== root) {
      if (node.getAttribute('class') === 'querylink') {
        url = node.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
        if ((node.tab && node.tab.isClosed) || (! node.tab)) {
          log('Opened ' + url);
          node.tab = jetpack.tabs.open(url);
        }
        node.tab.focus();
        break;
      }
      node = node.parentNode;
    }
  }, false);
}

function onContextMenuItemClick() {
  log("Selected '" + jetpack.selection.text + "' on " + jetpack.tabs.focused.url);
  updateSlidebar(function (slidebar) {
    addSlidebarEventListener(slidebar);
    slidebar.select();
  });
}

function onShowContextMenu(menu, context) {
  if (jetpack.selection.text) {
    initPackage(function (pkg) {
      menu.set({
        label: 'Query ' + pkg.name + ' for "' + jetpack.selection.text + '"',
        command: onContextMenuItemClick
      });
    });
  }
}

jetpack.menu.context.page.beforeShow = onShowContextMenu;

