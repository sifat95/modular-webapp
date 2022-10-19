import React, { Component } from 'react';
import keycloakService from '../services/keycloakService';

class Auth extends Component {

  state = {
    waitAuthCheck: true,
  };

  componentDidMount() {
    return Promise.all([
      // Comment the lines which you do not use
      this.keycloakCheck(),
    ]).then(() => {
      this.setState({ waitAuthCheck: false });
    });
  }

  keycloakCheck = () =>
    new Promise(resolve => {
      keycloakService.init(success => {
        if (!success) {
          resolve();
        } else if (success) {
          if (keycloakService.isAuthenticated()) {
            
            this.setState({ waitAuthCheck: false });
            this.props.showMessage({ message: 'Logging in with Keycloak' });
            
            keycloakService.getUserData().then(tokenData => {

              localStorage.setItem('userId', tokenData.sub);
              this.props.setUserDataKeycloak(tokenData);

              resolve();

              this.props.showMessage({ message: 'Logged in with Keycloak' });

            });
          } else {
            resolve();
          }
        }
      });
      return Promise.resolve();
    });

  render() {
    return this.state.waitAuthCheck ? (
      <FuseSplashScreen />
    ) : (
      <>{this.props.children}</>
    );
  }
}

export default Auth;
