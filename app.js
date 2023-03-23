// Select the HTML element with id signInButton and add an event listener to it
const signInButton = document.querySelector("#signInButton");
signInButton.addEventListener("click", initiateSignIn);

// Define the function that will be called when the signInButton is clicked
function initiateSignIn() {
  // Define the XUMM sign-in URL and the parameters that will be sent along with it
  const signUrl = "https://xumm.app/sign-in/request";
  const params = {
    txjson: {
      TransactionType: "SignIn"
    }
  };
  // Convert the parameters into a query string that can be appended to the URL
  const queryString = new URLSearchParams(params).toString();
  // Create the final sign-in URL by combining the URL and the query string
  const url = `${signUrl}?${queryString}`;
  
  // Open the sign-in URL in a new browser tab or window
  window.open(url, "_blank");
  
  // Listen for a message event that will be sent when the user signs in with XUMM
  window.addEventListener("message", receiveMessage, false);
}

// Define the function that will be called when the message event is received
function receiveMessage(event) {
  // Check that the message is coming from the XUMM app
  if (event.origin !== "https://xumm.app") {
    return;
  }
  
  // Get the data from the message
  const {data} = event;
  if (!data) {
    return;
  }
  
  // Check that the message is of the expected type
  if (data.type === "xumm.userToken") {
    // Parse the user token from the message data
    const {userToken} = data.payload;
    const jwt = parseJwt(userToken);
    const walletAddress = jwt.payload.payload.account;
    
    // Check the user's wallet balance and grant or deny access accordingly
    checkNft(walletAddress);
  }
}

// Define a function that will parse a JSON Web Token (JWT)
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

// Define a function that will check the user's wallet balance
function checkNft(walletAddress) {
  // Define the issuer address and taxon that we will use to check the wallet balance
  const issuerAddress = "<issuer-address>";
  const taxon = "<taxon>";
  
  // Define the API URL that we will use to check the wallet balance
  const apiUrl = `https://xrpl.org/s/${issuerAddress}/${taxon}?balances=${walletAddress}`;
  
  // Send a request to the API to get the wallet balance
  fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
      // Check the balance for the user's wallet address
      const balance = data.balances[walletAddress] || 0;
      if (balance > 0) {
        // If the balance is greater than 0, grant accessto the user
grantAccess();
} else {
// If the balance is 0, deny access to the user
denyAccess();
}
})
.catch((error) => {
console.error(error);
// If there was an error, deny access to the user
denyAccess();
});
}

// Define a function that will be called if the user has a non-zero balance
function grantAccess() {
// Show a success message to the user
alert("Access granted!");
}

// Define a function that will be called if the user has a zero balance or there was an error
function denyAccess() {
// Show an error message to the user
alert("Access denied. Please ensure that you have a balance of at least 1 NFT in your wallet.");
}
