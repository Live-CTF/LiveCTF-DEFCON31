
let API_ROOT = 'https://play.livectf.com/api'

let headers = new Headers();

let cookies = {};
document.cookie.split("; ").forEach((stuff) => {
  let pieces = stuff.split("=");
  cookies[pieces[0]] = pieces.slice(1).join("=");
});
console.log(cookies);

let $ticket = document.getElementById("ticket");
document.getElementById("ticket").value = cookies["ticket"] || "";
$ticket.addEventListener("change", () => {
  document.cookie = "ticket=" + $ticket.value;
  headers.set('X-LiveCTF-Token', $ticket.value);
  location.reload();
});

function getChallenges() {
  return fetch(API_ROOT + '/challenges', {
    headers: headers
  }).then((response) => {
    return response.json();
  });
}

function watchExploit(exploit) {
  // {
  //   "exploit_id": "b8844b32-ea8a-45cf-8666-569c1eb227fc",
  //   "team_id": 1,
  //   "challenge_id": 1001,
  //   "status": "Submitted",
  //   "score_awarded": null,
  //   "submission_time": "2023-05-26T21:36:40.006135238",
  //   "run_duration": null
  // }

  let $status = $("<span>")
      .text("Pending");

  let $li = $("<li>")
      .append(
          new Date(exploit.submission_time + "Z")
      )
      .append("&nbsp;")
      .append(
          $("<pre>").text(exploit.exploit_id)
              .css("display", "inline")
      )
      .append("&nbsp;")
      .append(
          $("<b>")
              .text("Status:")
      )
      .append("&nbsp;")
      .append($status);

  let $ul = $("ul#exploits-" + exploit.challenge_id);
  $ul.append($li);

  function updateExploit() {
    fetch(API_ROOT + "/exploits/" + exploit.exploit_id, {
      headers: headers
    }).then((response) => {
      return response.json().then((json) => {
        return {
          status: response.status,
          response: json
        }
      });
    }).then((response) => {
      if (response.status !== 200) {
        return Promise.reject("Error: " + response.response.error);
      }
      response = response.response;

      $status.text(response.status);
      // Submitted, Building, BuildOk, BuildFailed, Cancelled, Running, RunSolved, RunFailed
      if (response.status === "Submitted" || response.status === "Building" || response.status === "BuildOk" || response.status === "Running") {
        setTimeout(updateExploit, 5000);
      }

      if (response.status === "RunSolved") {
        $li.append("&nbsp;");
        $li.append($("<b>").text("Score:"));
        $li.append("&nbsp;");
        $li.append(response.score_awarded);
      }
    }).catch((error) => {
      $status.text(error);
    })
  }

  updateExploit();
}

function uploadExploit(challenge) {
  let file = $("#file-" + challenge.challenge_id);

  let body = new FormData();
  body.append('exploit', file[0].files[0]);

  return fetch(API_ROOT + '/challenges/' + challenge.challenge_id, {
    method: 'POST',
    headers: headers,
    body: body
  }).then((response) => {
    return response.json().then((json) => {
      return {
        status: response.status,
        response: json
      }
    });
  }).then((response) => {
    if (response.status !== 200) {
      return Promise.reject("Upload failed: " + response.response.error);
    }

    let exploits = JSON.parse(localStorage.getItem("exploits"));
    if (exploits === null) {
      exploits = [];
    }
    exploits.push(response.response);
    localStorage.setItem("exploits", JSON.stringify(exploits));

    watchExploit(response.response);
  }).catch((reason) => {
    alert("Upload failed: " + reason);
  });
}

function renderChallenge(challenge) {
  // {
  //   "challenge_id": 1001,
  //   "challenge_short_name": "live-test-1",
  //   "challenge_name": "livectf_challenge1",
  //   "releases_at": "2000-01-01T00:00:00",
  //   "closes_at": "2050-01-01T00:00:00"
  // }

  let child = $("<li>")
      .text(challenge.challenge_name + " ");

  child.append("<br>");
  child.append("Download Link: ")
  child.append(
      download = $("<a>")
      .attr("href", API_ROOT + '/challenges/' + challenge.challenge_id + '/download')
      .text('Download')
  );

  // Submit
  child.append("<br>");
  let closesAt = new Date(challenge.closes_at + "Z");
  let releasesAt = new Date(challenge.releases_at + "Z");
  if (new Date() > releasesAt && new Date() < closesAt) {
    child.append("Upload Exploit: ");

    let form = $("<div>")
        .attr("id", "upload-" + challenge.challenge_id);
    form.append(
        $("<input>")
            .attr("type", "file")
            .attr("id", "file-" + challenge.challenge_id)
    );
    form.append(
        $("<button>")
            .text("Upload")
            .click(() => uploadExploit(challenge))
    )

    child.append(form);
  }

  child.append(
      $("<ul>")
          .attr("id", "exploits-" + challenge.challenge_id)
  );
  child.append("<br>");

  return child;
}

function renderScoreboard() {
  let $availableScoreboard = $("#available-scoreboard");
  let $previousScoreboard = $("#previous-scoreboard");

  $availableScoreboard.empty();
  $previousScoreboard.empty();

  getChallenges().then((list) => {
    console.log(list);
    for (let challenge of list) {
      let closesAt = new Date(challenge.closes_at + "Z");
      if (new Date() > closesAt) {
        $previousScoreboard.append(renderChallenge(challenge));
      } else {
        $availableScoreboard.append(renderChallenge(challenge));
      }

    }
    let exploits = JSON.parse(localStorage.getItem('exploits'));
    if (exploits !== null) {
      for (let exploit of exploits) {
        watchExploit(exploit);
      }
    }
  });
}

if (cookies["ticket"] !== null) {
  headers.set('X-LiveCTF-Token', $ticket.value);
  renderScoreboard();
}
