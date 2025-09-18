/* === Carte VOYAGEUR (fallback si pas de prochain voyage) === */
function initVoyageurMap(opts){
  var defaultCenter = [0.39, 9.45]; // Libreville
  var divId = (opts && opts.mapDivId) ? opts.mapDivId : 'map-voyageur';
  var map = L.map(divId).setView(defaultCenter, 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);

  var routeLayer=null, driverMarker=null, trailLayer=null;
  var voyageId = (opts && opts.voyageId) ? parseInt(opts.voyageId,10) : 0;

  // ---- AUCUN prochain voyage : montrer une carte par défaut
  if(!voyageId){
    L.marker(defaultCenter).addTo(map).bindPopup("Aucun prochain voyage.<br>Carte centrée sur Libreville.").openPopup();
    return;
  }

  // ---- Avec voyageId : suivi normal
  fetch('/api/voyages/' + voyageId + '/state/', {credentials:'same-origin'})
    .then(function(r){ return r.json(); })
    .then(function(state){
      if(state && state.route_geojson){
        routeLayer = L.geoJSON(state.route_geojson).addTo(map);
        try{ map.fitBounds(routeLayer.getBounds(), {padding:[20,20]}); }catch(e){}
      }
    }).catch(console.error);

  function refresh(){
    fetch('/api/voyages/' + voyageId + '/state/', {credentials:'same-origin'})
      .then(function(r){ return r.json(); })
      .then(function(state){
        if(!state){ return; }
        if(state.last_point){
          var ll = [state.last_point.lat, state.last_point.lon];
          if(!driverMarker){ driverMarker = L.marker(ll).addTo(map); }
          else { driverMarker.setLatLng(ll); }
        }
        if(trailLayer){ map.removeLayer(trailLayer); }
        var pts = (state.recent_points||[]).map(function(p){ return [p.lat,p.lon]; });
        if(pts.length){ trailLayer = L.polyline(pts, {weight:4}).addTo(map); }
      }).catch(console.error);
  }
  setInterval(refresh, 5000); refresh();
}