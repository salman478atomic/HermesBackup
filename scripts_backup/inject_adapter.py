#!/usr/bin/env python3
"""Inject the RAWG adapter script block into ps3-game-library.html
right before </body>, and wire it into the two data-load paths."""
import re, sys

PATH = "/data/workspace/HermesBackup/ps3-game-library.html"
html = open(PATH, encoding="utf-8").read()

if "function rawgAdapter" in html:
    print("adapter already present — nothing to do")
    sys.exit(0)

ADAPTER = """<script>
/* ============================================================================
   RAWG ADAPTER v2 — normalizes RAWG-sourced records into the app schema.
   Runs on BOTH data paths: IndexedDB cache and remote fetch.
   Records already carrying "_adapter" are only de-duplicated (idempotent).
   ============================================================================ */
function rawgAdapter(list){
  var DLC_PAT = /(?::\\s*dlc\\b|\\bdlc\\b|\\bexpansion\\b|\\badd-?on\\b|\\bsoundtrack\\b|\\bskin pack\\b|\\bdeluxe bundle\\b|\\bseason pass\\b)/i;
  function num2(v){ var n=parseFloat(v); return isNaN(n)?null:n; }
  function parseEsrB(v){
    if(!v) return null;
    if(typeof v==="string"){ try{ v=JSON.parse(v); }catch(e){ return v; } }
    return (v && v.name) ? String(v.name) : null;
  }
  var ESRB_SHORT = { "everyone":"E", "everyone 10+":"E10+", "teen":"T", "mature":"M", "adults only":"AO", "rating pending":"RP" };
  function topSegment(s){
    var re=/\\{[^{}]*\\}/g, m, best=null, bestP=-1;
    while((m=re.exec(s||""))){
      var pm=/percent:\\s*([0-9.]+)/.exec(m[0]);
      var tm=/title:\\s*([a-z]+)/i.exec(m[0]);
      if(!pm||!tm) continue;
      var p=parseFloat(pm[1]);
      if(p>bestP){ bestP=p; best=tm[1].toLowerCase(); }
    }
    return best;
  }
  function dedupeKey(g){
    return g.title + "|" + (g.released||g.year||"") + "|" + (g._raw && g._raw.id);
  }
  var seen={}, out=[];
  (list||[]).forEach(function(r){
    if(!r) return;
    if(r._adapter){
      var k0=dedupeKey(r);
      if(!seen[k0]){ seen[k0]=1; out.push(r); }
      return;
    }
    var raw = r._raw || r;
    var name = raw.name || r.title || "(untitled)";
    var released = raw.released || r.released || "";
    var year = /^\\d{4}/.test(released) ? released.slice(0,4) : r.year;
    var tba = String(raw.tba===undefined?"":raw.tba).trim();
    if(tba==="1" || tba==="1.0" || tba==="true") year="TBA";
    var mc = num2(raw.metacritic);
    var us = num2(raw.rating);
    var top = num2(raw.rating_top) || 5;
    function pipe2comma(s){ return s ? String(s).split("|").join(", ") : null; }
    var parents = num2(raw.parents_count) || 0;
    var isDlc = parents>0 || DLC_PAT.test(name);
    var esrbName = parseEsrB(raw.esrb_rating);
    var contentRating = esrbName ? (ESRB_SHORT[String(esrbName).toLowerCase()] || esrbName) : r.content_rating;
    var g = {
      title: name,
      genres: pipe2comma(raw.genres) || r.genres || null,
      developer: pipe2comma(raw.developers) || r.developer || null,
      publisher: pipe2comma(raw.publishers) || r.publisher || null,
      platforms: pipe2comma(raw.platforms) || r.platforms || null,
      year: year,
      released: released || null,
      playtime: num2(raw.playtime),
      tags: pipe2comma(raw.tags) || r.tags || null,
      is_dlc: isDlc,
      critic_score: mc===null?null:Math.round(mc),
      user_score: us===null?null:Math.round((us/top)*1000)/10,
      critic_count: num2(raw.ratings_count)===null?null:Math.round(num2(raw.ratings_count)),
      user_score_count: num2(raw.reviews_text_count)===null?null:Math.round(num2(raw.reviews_text_count)),
      critic_sentiment: topSegment(raw.ratings),
      user_score_sentiment: topSegment(raw.ratings),
      content_rating: contentRating,
      series: r.series || null,
      achievements_count: num2(raw.achievements_count)===null?null:Math.round(num2(raw.achievements_count)),
      background_image: raw.background_image || r.background_image || null,
      website: raw.website || r.website || null,
      reddit_url: raw.reddit_url || r.reddit_url || null,
      metacritic_url: raw.metacritic_url || r.metacritic_url || null,
      description: (raw.description_raw || r.description || "").trim() || null,
      dlc_parent: null,
      _raw: raw,
      _adapter: 2
    };
    var k=dedupeKey(g);
    if(seen[k]) return;
    seen[k]=1;
    out.push(g);
  });
  return out;
}
</script>
"""

# 1) inject the adapter script before </body>
idx = html.rindex("</body>")
html = html[:idx] + ADAPTER + html[idx:]

# 2) wire into IndexedDB cache path
old_boot = """  idbAll().then(function(rows){
    if(rows && rows.length){
      dbg("loaded "+rows.length+" records from IndexedDB cache");
      bootWithData(rows);"""
new_boot = """  idbAll().then(function(rows){
    if(rows && rows.length){
      rows = rawgAdapter(rows);
      dbg("loaded "+rows.length+" records from IndexedDB cache (RAWG-normalized)");
      bootWithData(rows);"""
assert old_boot in html, "boot anchor not found"
html = html.replace(old_boot, new_boot)

# 3) wire into remote fetch path
old_api = """    .then(function(j){
      var list = Array.isArray(j) ? j : (j && Array.isArray(j.games) ? j.games : null);
      if(!list) throw new Error("unexpected JSON shape");
      dbg("received "+list.length+" records");
      return idbPut(list).then(function(){ return list; });"""
new_api = """    .then(function(j){
      var list = Array.isArray(j) ? j : (j && Array.isArray(j.games) ? j.games : null);
      if(!list) throw new Error("unexpected JSON shape");
      list = rawgAdapter(list);
      dbg("received "+list.length+" records (RAWG-normalized)");
      return idbPut(list).then(function(){ return list; });"""
assert old_api in html, "api anchor not found"
html = html.replace(old_api, new_api)

open(PATH, "w", encoding="utf-8").write(html)
print("adapter injected + both load paths wired")
print("rawgAdapter occurrences:", html.count("rawgAdapter"))
