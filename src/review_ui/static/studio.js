/* ==================================================================
   Animation Studio — realtime UI client.
   Approve / reject / promote / shortlist / regenerate update the
   state chip in place via the JSON API; the dashboard polls overview,
   jobs and the activity log.
   ================================================================== */
(function () {
  "use strict";

  var PENDING_STATES = ["scored", "generated", "shortlisted"];

  /* ------------------------------------------------------------------
     Toasts
     ------------------------------------------------------------------ */
  var toastContainer = document.getElementById("toast-container");

  function toast(message, type) {
    if (!toastContainer) return;
    var el = document.createElement("div");
    el.className = "toast toast-" + (type || "info");
    el.textContent = message;
    toastContainer.appendChild(el);
    setTimeout(function () {
      el.classList.add("toast-out");
      setTimeout(function () { el.remove(); }, 300);
    }, 2600);
  }

  /* ------------------------------------------------------------------
     State chips
     ------------------------------------------------------------------ */
  function findCard(node) {
    while (node && node !== document.body) {
      if (node.dataset && node.dataset.assetId) return node;
      node = node.parentElement;
    }
    return null;
  }

  function updateState(card, state) {
    if (!card) return;
    card.dataset.state = state;
    card.querySelectorAll(".asset-state").forEach(function (chip) {
      chip.className = "asset-state state-" + state;
      chip.textContent = state;
    });
    var reviewed = PENDING_STATES.indexOf(state) === -1;
    if (reviewed) {
      card.classList.add("asset-reviewed");
      card.querySelectorAll("[data-action]").forEach(function (btn) {
        btn.disabled = true;
      });
    }
  }

  /* ------------------------------------------------------------------
     Action handling (delegated)
     ------------------------------------------------------------------ */
  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-action]");
    if (!btn || btn.disabled) return;

    var card = findCard(btn);
    if (!card) return;

    var assetId = card.dataset.assetId;
    var action = btn.dataset.action;
    var reasonInput = btn.parentElement
      ? btn.parentElement.querySelector("[data-reason]")
      : null;
    var reason = reasonInput ? reasonInput.value : "";

    btn.disabled = true;

    var body = new FormData();
    if (reason) body.append("reason", reason);

    fetch("/api/assets/" + encodeURIComponent(assetId) + "/" + encodeURIComponent(action), {
      method: "POST",
      body: body,
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.ok) {
          btn.disabled = false;
          toast(data.error || data.message || "Action failed", "error");
          return;
        }
        toast(data.message, "success");
        if (data.state) updateState(card, data.state);
        refreshOverview();
        refreshLog();
      })
      .catch(function () {
        btn.disabled = false;
        toast("Network error — action not applied", "error");
      });
  });

  /* ------------------------------------------------------------------
     Activity log polling
     ------------------------------------------------------------------ */
  var logList = document.getElementById("log-list");

  function renderLog(entries) {
    if (!logList) return;
    logList.innerHTML = "";
    if (!entries || !entries.length) {
      var li = document.createElement("li");
      li.className = "log-line log-empty";
      li.textContent = "No activity yet.  Generate or seed to see progress here.";
      logList.appendChild(li);
      return;
    }
    entries.slice(-50).forEach(function (e) {
      var line = document.createElement("li");
      line.className = "log-line log-" + (e.level || "").toLowerCase();
      var t = document.createElement("span");
      t.className = "log-time";
      t.textContent = e.time || "";
      var l = document.createElement("span");
      l.className = "log-level";
      l.textContent = e.level || "";
      var m = document.createElement("span");
      m.className = "log-msg";
      m.textContent = e.message || "";
      line.appendChild(t); line.appendChild(l); line.appendChild(m);
      logList.appendChild(line);
    });
  }

  function refreshLog() {
    if (!logList) return Promise.resolve();
    return fetch("/logs")
      .then(function (r) { return r.json(); })
      .then(function (data) { renderLog(data.entries || []); })
      .catch(function () {});
  }

  /* ------------------------------------------------------------------
     Overview polling (dashboard counters)
     ------------------------------------------------------------------ */
  function refreshOverview() {
    var targets = {
      "ov-entities": "total_entities",
      "ov-assets": "total_assets",
      "ov-pending": "pending",
      "ov-approved": "approved",
      "ov-production": "production",
    };
    var present = Object.keys(targets).some(function (id) {
      return document.getElementById(id);
    });
    if (!present) return Promise.resolve();
    return fetch("/api/overview")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        Object.keys(targets).forEach(function (id) {
          var el = document.getElementById(id);
          if (el && data[targets[id]] !== undefined) el.textContent = data[targets[id]];
        });
      })
      .catch(function () {});
  }

  /* ------------------------------------------------------------------
     Jobs polling (dashboard table)
     ------------------------------------------------------------------ */
  var jobList = document.getElementById("job-list");

  function renderJobs(jobs) {
    if (!jobList) return;
    jobList.innerHTML = "";
    if (!jobs || !jobs.length) {
      var tr = document.createElement("tr");
      tr.innerHTML = '<td colspan="5"><p class="empty-state">No generation jobs yet.</p></td>';
      jobList.appendChild(tr);
      return;
    }
    jobs.slice(0, 10).forEach(function (j) {
      var tr = document.createElement("tr");
      var tdId = document.createElement("td");
      var code = document.createElement("code");
      code.textContent = j.id || "";
      tdId.appendChild(code);
      var tdChar = document.createElement("td");
      tdChar.textContent = j.character_id || "";
      var tdType = document.createElement("td");
      tdType.textContent = j.job_type || "";
      var tdStatus = document.createElement("td");
      var badge = document.createElement("span");
      badge.className = "badge badge-" + (j.status || "");
      badge.textContent = j.status || "";
      tdStatus.appendChild(badge);
      var tdCreated = document.createElement("td");
      tdCreated.textContent = j.created_at || "";
      tr.appendChild(tdId); tr.appendChild(tdChar); tr.appendChild(tdType);
      tr.appendChild(tdStatus); tr.appendChild(tdCreated);
      jobList.appendChild(tr);
    });
  }

  function refreshJobs() {
    if (!jobList) return Promise.resolve();
    return fetch("/api/jobs")
      .then(function (r) { return r.json(); })
      .then(function (data) { renderJobs(data.jobs || []); })
      .catch(function () {});
  }

  /* ------------------------------------------------------------------
     Start polling
     ------------------------------------------------------------------ */
  setInterval(refreshLog, 2000);
  setInterval(refreshOverview, 3000);
  setInterval(refreshJobs, 3000);
})();
