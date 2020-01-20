// AJK 13 September
// Dereived from Google Firebase login example
// https://firebase.googleblog.com/2017/02/auth-flows-with-firebase-ui-on-web.html

$(function(){
  // var backendHostUrl = 'http://localhost:8081';
  var backendHostUrl = 'http://mimas-aotb.appspot.com';

  // This is passed into the backend to authenticate the user.
  var userIdToken = null;

  // Firebase log-in
  function configureFirebaseLogin() {
    firebase.initializeApp(firebase_config);
    firebase.auth().onAuthStateChanged(function(user) {

      if (user) {
        $('#logged-out').hide();
        var name = user.displayName;
        var welcomeName = name ? name : user.email;

        user.getToken().then(function(idToken) {
          userIdToken = idToken;

            window.location.replace("/fireloggedin?user=" + userIdToken)
              $('#user').text(welcomeName);
              $('#logged-in').show();
        });

      } else {
        $('#logged-in').hide();
        $('#logged-out').show();
      }
    });
  }

  function configureFirebaseLoginWidget() {
    var uiConfig = {
      'signInSuccessUrl': '/fireloggedin',
      'signInOptions': [
        firebase.auth.GoogleAuthProvider.PROVIDER_ID,
        firebase.auth.FacebookAuthProvider.PROVIDER_ID,
        firebase.auth.EmailAuthProvider.PROVIDER_ID
      ],
      // Terms of service url
      'tosUrl': 'http://mimas-aotb.appspot.com/',
    };

    var ui = new firebaseui.auth.AuthUI(firebase.auth());
    ui.start('#firebaseui-auth-container', uiConfig);
  }

  configureFirebaseLogin();
  configureFirebaseLoginWidget();
});
