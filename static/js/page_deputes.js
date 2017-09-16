var groupe = "ALL";
var tri="depute_nom_tri";
var dir="1";
var searchtext="";
var region= "ALL";
var infScroll;
var elem = document.getElementById('depute-liste');

function setInfiniteScroll(){
  if (infScroll!=undefined) {
      elem.innerHTML = "";
      infScroll.destroy()
  }
  infScroll = new InfiniteScroll( elem, {
  // options
  path: 'deputes_ajax/{{#}}/'+groupe+'/'+tri+'/'+dir+'/?search='+searchtext+'&region='+region,
  checkLastPage: '.pagination__next',
  append: '.depute-item',
  history: false,
  prefill: true
  });
}
var groupesel = document.getElementById("deputes-groupe-filter");
groupesel.addEventListener("change", function() { groupe = this.value; setInfiniteScroll(); console.log(groupe);});
var regionsel = document.getElementById("deputes-region-filter");
regionsel.addEventListener("change", function() { region = this.value; setInfiniteScroll(); console.log(region);});
var sortsel = document.getElementById("deputes-sort");
sortsel.addEventListener("change", function() { tri = this.value; setInfiniteScroll(); console.log(tri);});
var dirsel = document.getElementById("deputes-sortdir");
dirsel.addEventListener("change", function() { dir = this.value; setInfiniteScroll(); console.log(dir);});
var search = document.getElementById("deputes-searchbutton");
search.addEventListener("click", function() {
        searchtext = document.getElementById("deputes-searchtext").value;
        setInfiniteScroll(); console.log(searchtext);
});
var searchButton = document.getElementById("deputes-searchtext");
searchButton.addEventListener("keypress", function(e) {
     if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
          searchtext = document.getElementById("deputes-searchtext").value;
        setInfiniteScroll(); console.log(searchtext);
     }
});

setInfiniteScroll();
