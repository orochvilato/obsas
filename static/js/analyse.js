var pushURL = function() {
    var params = {};
    
    params.desc = current_desc;
    params.axe = current_axe;
    params.suffrages = current_suffrages;
    params.filtres = current_filtres;
    params.tri = current_tri;
    var str = jQuery.param( params );
    window.history.pushState("string", "obsas", "analyse?"+str);
    console.log(str);
}

var updateView = function() {
    console.log('updateview');
    $('.updateview').unbind('change');
    $('#sens').unbind('click');
    var suffrages = $('select#suffrages').val();
    var tri = $('select#tri').val();
    var axe = $('select#axe').val();
    var filtres;

    var params = {};
    
    if (current_desc != undefined) {
        params.desc = current_desc;
    }
    if (axe != undefined) {
        params.axe = axe;
        current_axe = axe;
    } else {
        params.axe = current_axe;
    }
    if (filtres!= undefined) {
        params.filtres = filtres;
        current_filtres = filtres;
    } else {
        params.filtres = JSON.stringify(current_filtres);
    }
    if (suffrages != undefined) {
        params.suffrages = suffrages;
        current_suffrages = suffrages;
    } else {
        params.suffrages = current_suffrages;
    }
    if (tri != undefined) {
        params.tri = tri;
        current_tri = tri;
    } else {
        params.tri = current_tri;
    }
    
    $.LoadingOverlay("show");
    $.ajax({
    url: 'analyse/vueaxe',
    data: params,
    type: 'GET',
    dataType: 'html'
  }).done(function(data) {
      $.LoadingOverlay("hide");
      $('#vue').html(data);
      $('select').material_select();
      $('.updateview').change(function() {
        console.log('select');
          updateView();
      });
      $('#sens').click(function() {
          console.log('desc');
          current_desc = 1-current_desc;
          updateView();
      });
      pushURL();
      
  });
};

$(document).ready( function() {
    console.log('docready');
    updateView();
});
