var pushURL = function() {
    var params = {};
    
    params.desc = current_desc;
    params.axe = current_axe;
    params.suffrages = current_suffrages;
    params.filtres = JSON.stringify(current_filtres);
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
         updateView();
      });
      $('#sens').click(function() {
          current_desc = 1-current_desc;
          updateView();
      });
      $('#filtresaxe').change(function() {
          console.log('change');
          var show = $(this).val();
          $.each(axes,function(i,axe) {
              console.log('show',show,axe,show);
              if (show.indexOf(axe)>=0) {
                  console.log($('select.filtreaxe[axe="+axe+"]'));
                  $('#filtre_'+axe).show();
                  if (!(axe in current_filtres)) {
                      current_filtres[axe] = [];
                  }
              } else {
                  $('#filtre_'+axe).hide();
                  current_filtres[axe] = [];
                  $('#filtresel_'+axe+' option').prop('selected',false);
              }
          });
      });
      $('#filtrer').click(function() {
          var newfilter = {}
          $('.filtreaxe').each(function() {
              var a = $(this).attr('axe');
              var v = $(this).val();
              if (a && v.length>0) {
                  newfilter[a] = v;
              }
          });
          console.log(newfilter);
          current_filtres = newfilter;
          updateView();
      });
      pushURL();
      
  });
};

$(document).ready( function() {
    console.log('docready');
    updateView();
});
