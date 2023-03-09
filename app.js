const signInButton = document.querySelector("#signInButton");
signInButton.addEventListener("click", initiateSignIn);

function initiateSignIn() {
  const signUrl = "https://xumm.app/sign-in/request";
  const params = {
    txjson: {
      TransactionType: "SignIn"
    }
  };
  const queryString = new URLSearchParams(params).toString();
  const url = `${signUrl}?${queryString}`;
  
  window.open(url, "_blank");
  
  window.addEventListener("message", receiveMessage, false);
}

function receiveMessage(event) {
  if (event.origin !== "https://xumm.app") {
    return;
  }
  
  const {data} = event;
  if (!data) {
    return;
  }
  
  if (data.type === "xumm.userToken") {
    const {userToken} = data.payload;
    const jwt = parseJwt(userToken);
    const walletAddress = jwt.payload.payload.account;
    
    checkNft(walletAddress);
  }
}

function parseJwt(token) {
  const base64Url = token.split(".")[1];
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split("")
      .map(function (c) {
        return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
      })
      .join("")
  );
  return JSON.parse(jsonPayload);
}

function checkNft(walletAddress) {
  const issuerAddress = "<issuer-address>";
  const taxon = "<taxon>";
  
  const apiUrl = `https://xrpl.org/s/${issuerAddress}/${taxon}?balances=${walletAddress}`;
  
  fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
      const balance = data.balances[walletAddress] || 0;
      if (balance > 0) {
        grantAccess();
      } else {
        denyAccess();
      }
    })
    .catch((error) => {
      console.error(error);
      denyAccess();
    });
}

function grantAccess() {
  alert("Access granted!"); // Replace with your actual code to allow access
}

function denyAccess() {
  alert("Access denied!"); // Replace with your actual code to deny access
}
