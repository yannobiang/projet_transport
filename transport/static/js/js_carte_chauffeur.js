/* === Carte CHAUFFEUR (fallback si pas de voyage) === */
function getCookie(name){
  var m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return m ? m.pop() : '';
}
function jsonGet(url){ return fetch(url, { credentials:'same-origin' }).then(function(r){ return r.json(); }); }

function initChauffeurMap(opts){
  var defaultCenter = [0.39, 9.45]; // Libreville
  var divId = (opts && opts.mapDivId) ? opts.mapDivId : 'map-chauffeur';
  var map = L.map(divId).setView(defaultCenter, 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19}).addTo(map);

  var routeLayer=null, trailLayer=null, driverMarker=null;
  var voyageId = (opts && opts.voyageId) ? parseInt(opts.voyageId,10) : 0;

  // ---- PAS DE VOYAGE : afficher une carte "statique"
  if(!voyageId){
    L.marker(defaultCenter).addTo(map).bindPopup("Aucun voyage en cours.<br>Carte centrée sur Libreville.").openPopup();
    return; // rien à suivre
  }

  // ---- Avec voyageId : on suit normalement
  jsonGet('/api/voyages/' + voyageId + '/state/')
    .then(function(state){
      if(state && state.route_geojson){
        routeLayer = L.geoJSON(state.route_geojson).addTo(map);
        try{ map.fitBounds(routeLayer.getBounds(), {padding:[20,20]}); }catch(e){}
      }
    }).catch(console.error);

  function pushPosition(pos){
    var c = pos.coords;
    fetch('/api/push-position/', {
      method:'POST',
      headers:{'Content-Type':'application/json','X-CSRFToken': getCookie('csrftoken')},
      credentials:'same-origin',
      body:JSON.stringify({
        voyage_id: voyageId,
        lat:c.latitude, lon:c.longitude,
        accuracy_m:c.accuracy,
        captured_at:new Date(pos.timestamp).toISOString()
      })
    }).catch(console.warn);
  }
  if(navigator.geolocation){
    navigator.geolocation.watchPosition(pushPosition, function(e){console.warn(e.message);},
      {enableHighAccuracy:true, maximumAge:5000, timeout:15000});
  }

  function refresh(){
    jsonGet('/api/voyages/' + voyageId + '/state/')
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

  // (option) tu peux laisser la couche POI ici si tu veux
}