var compare_axe = undefined;
var compare_item = undefined;
var axes;
var scrutins = [];
var filtres_axes=[];
var current_axe = 0;
var current_desc = 1;
var current_elements = [];
var exprimes = true;

var updateView = function() {
    var suffrages = $('select#suffrages').val();
    var tri = $('select#tri').val();
    var axe = $('select#axe').val();
    
    var params = {};
    
    if (current_desc != undefined) {
        params.desc = current_desc;
    }
    if (axe != undefined) {
        params.axe = axe;
    }
    if (suffrages != undefined) {
        params.suffrages = suffrages;
    }
    if (tri != undefined) {
        params.tri = tri;
    }
    console.log(params);
    $.ajax({
    url: 'analyse/vueaxe',
    data: params,
    type: 'GET',
    dataType: 'html'
  }).done(function(data) {
      $('#vue').html(data);
      $('select').material_select();
      $('.updateview').change(function() {
        updateView();
      });
      $('#sens').click(function() {
          current_desc = 1-current_desc;
          updateView();
      });
  });
};

$(document).ready( function() {
    updateView();
});