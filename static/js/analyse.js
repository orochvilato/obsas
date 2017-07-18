var pushURL = function() {
    var params = {};
    
    params.desc = current_desc;
    params.axe = current_axe;
    params.suffrages = current_suffrages;
    params.filtresaxes = JSON.stringify(current_filtresaxes);
    params.filtresitems = JSON.stringify(current_filtresitems);
    params.tri = current_tri;
    params.filterson = 1;
    var str = jQuery.param( params );
    window.history.pushState("string", "obsas", "analyse?"+str);
    console.log(str);
}

var updateView = function() {
    
    $('.updateview').unbind('change');
    $('#sens').unbind('click');
    var suffrages = $('select#suffrages').val();
    var tri = $('select#tri').val();
    var axe = $('select#axe').val();
    
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
    params.filtresaxes = JSON.stringify(current_filtresaxes);
    params.filtresitems = JSON.stringify(current_filtresitems);
    params.filterson = filterson;
    
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
    console.log(params);
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
      $('.itemfilter').click(function() {
          var a=$(this).attr('axe');
          var it=$(this).attr('item');
          console.log(current_filtresaxes);
          if (current_filtresaxes[a]==undefined) {
                current_filtresaxes[a]==[];
          }
          var idx=current_filtresaxes[a].indexOf(it);
          if (idx<0) {
              current_filtresaxes[a].push(it);
              $(this).addClass('filtered');
          } else {
              current_filtresaxes[a].splice(idx, 1);
              $(this).removeClass('filtered');
              if (current_filtresaxes[a].length==0) {
                  delete current_filtresaxes[a]
              }
              
          }
          updateView();
      });
      $('#sens').click(function() {
          current_desc = 1-current_desc;
          updateView();
      });
      $('#showanalyse').click(function() {
          filterson = 1-filterson;
          $('.analyse').toggle();
      });
      $('#filtresaxe').change(function() {
          var show = $(this).val();
          $.each(axes,function(i,axe) {
              console.log('show',show,axe,show);
              if (show.indexOf(axe)>=0) {
                  console.log($('select.filtreaxe[axe="+axe+"]'));
                  $('#filtre_'+axe).show();
                  if (!(axe in current_filtresaxes)) {
                      current_filtresaxes[axe] = [];
                  }
              } else {
                  $('#filtre_'+axe).hide();
                  current_filtresaxes[axe] = [];
                  $('#filtresel_'+axe+' option').prop('selected',false);
              }
          });
      });
      $('#filtresitem').change(function() {
          
          var show = $(this).val();
          
          $.each(filtresitm,function(i,fitem) {
              console.log(fitem);
              var min = parseInt($('#f'+fitem).val('min'));
              var max = parseInt($('#f'+fitem).val('max'));
              if (show.indexOf(fitem)>=0) {
                  
                  $('#filtreit_'+fitem).show();
                  if (!(fitem in current_filtresitems)) {
                      current_filtresitems[fitem] = [min,max];
                      $('#f'+fitem).get(0).noUiSlider.set([min,max]);
                  }
              } else {
                  $('#filtreit_'+fitem).hide();
                  $('#f'+fitem).get(0).noUiSlider.set([min,max]);
                  delete current_filtresitems[fitem];
              }
          });
      });

      $('#filtrer').click(function() {
          var newfilteraxe = {};
          var newfilteritem = {};
          $('.filtreaxe').each(function() {
              var a = $(this).attr('axe');
              var v = $(this).val();
              if (a && v.length>0) {
                  newfilteraxe[a] = v;
              }
          });
          $('.pctslider').each(function() {
              var f = $(this).attr('f');
              if (f in current_filtresitems) {
                  v = $(this).get(0).noUiSlider.get();
                  newfilteritem[f] = [parseInt(v[0]),parseInt(v[1])];
              }
          });
          
          current_filtresaxes = newfilteraxe;
          current_filtresitems = newfilteritem;
          console.log(current_filtresitems);
          updateView();
      });
      $('.pctslider').each(function() {
          console.log('slider');
          var id = $(this).attr('id');
        
         
          //var slider = document.getElementById('fparticipation');
          var _max = $(this).attr('max');
          var _min = $(this).attr('min');
          var _vmax = $(this).attr('vmax');
          var _vmin = $(this).attr('vmin');
         
          if (_vmax == undefined) {
              _vmax = _max;
          }
          if (_vmin == undefined) {
              _vmin = _min;
          }
          var min = parseInt(_min);
          var vmin = parseInt(_vmin);
          var max = parseInt(_max);
          var vmax = parseInt(_vmax);
          console.log(min,max,vmin,vmax);
          noUiSlider.create(this, {
              start: [vmin, vmax],
              connect: true,
              step: 5,
              range: {
             'min': min,
             'max': max
           },
         });
        
        
        var handles = [ document.getElementById(id+'-min'), document.getElementById(id+'-max') ]
        this.noUiSlider.on('update', function( values, handle ) {
            var val = Math.round(values[handle])
            
            
            handles[handle].innerHTML = val;
        });
      });
      if (filterson==1) {
          pushURL();
      }
  });
};

$(document).ready( function() {
    console.log('docready');
    updateView();
});
