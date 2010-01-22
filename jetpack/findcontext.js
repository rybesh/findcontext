/*jslint eqeqeq: true, immed: true, newcap: true, nomen: true, onevar: true, passfail: true, plusplus: true, regexp: true, undef: true, white: true, indent: 2*/
/*global jetpack, console, $ */

jetpack.future.import('menu');
jetpack.future.import('selection');
jetpack.future.import("slideBar");

SIDEBAR_URI = 'http://127.0.0.1:8000/sidebar'
API_URI = 'http://127.0.0.1:8000/api'

var pkg = null;
var slidebar = null;

function initPackage(callback) {
  if (pkg) {
    callback(pkg);
  } else {
    $.getJSON(API_URI + '/package/', function(packages) {
      pkg = packages[0]; // TODO: allow user to select
      callback(pkg);
    });
  }
}

function updateSlidebar(callback) {
  var content = (SIDEBAR_URI + '?p=' + pkg.uri + '&q=' + escape(jetpack.selection.text));
  if (slidebar) {
    slidebar.contentDocument.location = content;
    callback(slidebar);
  } else {
    jetpack.slideBar.append({
      url: content,
      width: 250,
      persist: true,
      onReady: function(slbr) {
        slidebar = slbr;
        callback(slidebar);
      }
    });
  }
}

function onContextMenuItemClick() {
  updateSlidebar(function(slidebar) {
    var root = slidebar.contentDocument.rootElement;
    root.addEventListener('mousedown', function(event) {
      var node = event.target;
      while (node !== root) {
        if (node.getAttribute('class') === 'querylink') {
          var url = node.getAttributeNS('http://www.w3.org/1999/xlink', 'href');
          if ((node.tab && node.tab.isClosed) || (! node.tab)) {
            node.tab = jetpack.tabs.open(url);
          }
          node.tab.focus();
          break;
        }
        node = node.parentNode;
      }
    }, false);
    slidebar.select();
  });
}

function onShowContextMenu(menu, context) {
  if (jetpack.selection.text) {
    initPackage(function(pkg) {
      menu.set({
        label: 'Query ' + pkg.name + ' for "' + jetpack.selection.text + '"',
        command: onContextMenuItemClick
      });
    });
  }
}

jetpack.menu.context.page.beforeShow = onShowContextMenu;
