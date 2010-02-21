/*jslint eqeqeq: true, immed: true, newcap: true, nomen: true, onevar: true, passfail: true, plusplus: true, regexp: true, undef: true, white: true, indent: 2*/
/*global jetpack, console, encodeURIComponent, $ */

jetpack.future.import('menu');
jetpack.future.import('selection');
jetpack.future.import("slideBar");

var BASE_URI = 'http://127.0.0.1:8000/'; //'http://{{ request.get_host }}/'
var SIDEBAR_URI = BASE_URI + 'sidebar/';
var API_URI = BASE_URI + 'api/';
var USER = 'user01'; //'{{ user.username }}';
var PASS = 'celt138';

var pkg = null;
var slidebar = null;
var selection = null;

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
    'beforeSend': function (request) {
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
  var content = (SIDEBAR_URI + '?p=' + pkg.uri + '&q=' + encodeURIComponent(selection));
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

function trackTab(doc) {
  if (! doc.defaultView.frameElement) { 
    if (doc.referrer) {
      log('Opened ' + this.url + ' (via ' + doc.referrer + ')');
    } else if (this.url === this.start_url) { 
      log('Opened ' + this.url);
    } else { // stop tracking this tab
      this.onReady.unbind(trackTab);
    }
  }  
}

function addClass(elem, value) {
  var class_names, old_class, new_class, c, cl;
  class_names = (value || "").split(/\s+/);
  if (! elem.getAttribute('class')) {
    elem.setAttribute('class', value);
  } else {
    old_class = ' ' + elem.getAttribute('class') + ' ';
    new_class = elem.getAttribute('class');
    for (c = 0, cl = class_names.length; c < cl; c += 1) {
      if (old_class.indexOf(' ' + class_names[c] + ' ') < 0) {
        new_class += ' ' + class_names[c];
      }
    }
    elem.setAttribute('class', new_class);
  }
}

function hasClass(elem, value) {
  return ((' ' + elem.getAttribute('class') + ' '
          ).indexOf(' ' + value + ' ') > -1 )
}

function addSlidebarEventListener(slidebar) {
  var root, node, url;
  root = slidebar.contentDocument.rootElement;
  root.addEventListener('mousedown', function (event) {
    node = event.target;
    while (node !== root) {
      if (hasClass(node, 'querylink')) {
        url = node.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
        node.tab = jetpack.tabs.open(url);
        node.tab.start_url = url;
        node.tab.onReady(trackTab);
        node.tab.focus();
        break;
      }
      node = node.parentNode;
    }
  }, false);
}

function testQueries(slidebar) {
  /* Check queries to see if they have no results. 
   * Wait a random interval between queries to avoid
   * tripping the automated query detector at GOOG. */
  var no_results, random_wait, delay, delays = [];
  no_results = /Your search - <b>[^<]*<\/b> - did not match any documents\./;
  Array.forEach(
    slidebar.contentDocument.getElementsByClassName('querylink'),
    function (link, i) { 
      let url = link.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
      random_wait = (Math.random() * 1000); // 0 to 1 seconds
      if (i === 0) {
        delay = random_wait;
      } else {
        delay = delays[i - 1] + random_wait;
      }
      delays.push(delay);
      setTimeout(function () {
        $.get(url, function (data) {
          if (no_results.test(data)) {
            addClass(link, 'noresults');
          } else {
            addClass(link, 'results');
          }
        });
      }, delay);
    }
  );
}

function onContextMenuItemClick() {
  log("Selected '" + selection + "' on " + jetpack.tabs.focused.url);
  updateSlidebar(function (slidebar) {
    addSlidebarEventListener(slidebar);
    slidebar.select();
    testQueries(slidebar);
  });
}

function onShowContextMenu(menu, context) {
  if (jetpack.selection.text) {
    selection = jetpack.selection.text;
    initPackage(function (pkg) {
      menu.set({
        label: 'Query ' + pkg.name + ' for "' + selection + '"',
        command: onContextMenuItemClick
      });
    });
  }
}

jetpack.menu.context.page.beforeShow = onShowContextMenu;

