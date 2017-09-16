var deputes_groupe = "ALL";
var deputes_tri="depute_nom_tri";
var deputes_dir="1";
var deputes_searchtext="";
var deputes_region= "ALL";
var deputes_top="";
var infScroll;
var elem = document.getElementById('depute-liste');

function setInfiniteScroll(){
  if (infScroll!=undefined) {
      elem.innerHTML = "";
      infScroll.destroy()
  }
  infScroll = new InfiniteScroll( elem, {
  // options
  path: 'deputes_ajax/{{#}}?gp='+deputes_groupe+'&tr='+deputes_tri+'&di='+deputes_dir+'&txt='+deputes_searchtext+'&rg='+deputes_region+'&top='+deputes_top,
  checkLastPage: '.pagination__next',
  append: '.depute-item',
  history: false,
  prefill: true
  });
}
var groupesel = document.getElementById("deputes-groupe-filter");
groupesel.addEventListener("change", function() { deputes_groupe = this.value; setInfiniteScroll(); });
var regionsel = document.getElementById("deputes-region-filter");
regionsel.addEventListener("change", function() { deputes_region = this.value; setInfiniteScroll(); });
var topsel = document.getElementById("deputes-top-filter");
topsel.addEventListener("change", function() { deputes_top = this.value; setInfiniteScroll(); });
var sortsel = document.getElementById("deputes-sort");
sortsel.addEventListener("change", function() { deputes_tri = this.value; setInfiniteScroll(); });
var dirsel = document.getElementById("deputes-sortdir");
dirsel.addEventListener("change", function() { deputes_dir = this.value; setInfiniteScroll(); });
var search = document.getElementById("deputes-searchbutton");
function launchSearch() {
        deputes_searchtext = document.getElementById("deputes-searchtext").value;
        setInfiniteScroll(); 
}
search.addEventListener("click", launchSearch );
var searchButton = document.getElementById("deputes-searchtext");
searchButton.addEventListener("keypress", function(e) {
     if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
          launchSearch();
     }
});

setInfiniteScroll();
