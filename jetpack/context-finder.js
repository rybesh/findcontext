/*jslint eqeqeq: true, immed: true, newcap: true, nomen: true, onevar: true, passfail: true, plusplus: true, regexp: true, undef: true, white: true, indent: 2*/
/*global jetpack, console, $ */

jetpack.future.import('menu');
jetpack.future.import('selection');
jetpack.future.import("slideBar");

SIDEBAR_URI = 'http://127.0.0.1:8000/sidebar/'

var slidebar = null;

var pkg = {
  id: 'test',
  name: 'CS 138 Resources'
};

function onSlideBarReady(slbr) {
  slidebar = slbr;
  slidebar.select();
}

function onContextMenuItemClick() {
  /*
  pkg.resources.forEach(function (resource) {
    jetpack.tabs.open(
      Template.expand(
        resource.template, { query: jetpack.selection.text }));
  });
  */
  var sidebar_location = (
    SIDEBAR_URI + pkg.id + '?q=' + escape(jetpack.selection.text));
  if (slidebar) {
    slidebar.contentDocument.location = sidebar_location;
    slidebar.select();
  } else {
    jetpack.slideBar.append({
      url: sidebar_location,
      width: 210,
      persist: true,
      onReady: onSlideBarReady
    });
  }
}

function onShowContextMenu(menu, context) {
  if (jetpack.selection.text) {
    menu.set({
      label: 'Query ' + pkg.name + ' for "' + jetpack.selection.text + '"',
      command: onContextMenuItemClick
    });
  }
}

jetpack.menu.context.page.beforeShow = onShowContextMenu;
