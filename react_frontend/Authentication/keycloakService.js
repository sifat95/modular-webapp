import Keycloak from "keycloak-js";
import KcAdminClient from 'keycloak-admin';
import credentialRadassistAdmin from './keycloakAdminCredentials';

const configToken = {
	baseUrl: 'https://dev.radassist.net/auth',
	realmName: 'radassist',
}

class KeycloakService {
    
    state = {
        keycloak: null,
        isAuthenticated: false,
		kcAdminClient: null,
		expiresAt: null
    };
	
	init(success) {
        const keycloak = Keycloak('/keycloak.json');
        const kcAdminClient = new KcAdminClient(configToken);

		keycloak.init({ onLoad: "login-required","checkLoginIframe" : false }).then(async authenticated => {
            this.state.keycloak = keycloak;
			this.state.isAuthenticated = authenticated;
			
			if(authenticated) {
				kcAdminClient.auth(
					credentialRadassistAdmin.credentialRadassistAdmin
				).then(()=>{
					this.state.kcAdminClient = kcAdminClient;
					success(true);
				});
			}
        });
	}

	isAuthenticated (){
		if (this.state.isAuthenticated) {
			return true;
		}
		// Check whether the current time is past the
		// access token's expiry time
		
		return false;
	};

	getUserData = () => {
		return new Promise((resolve, reject) => {
			const tokenData = this.state.keycloak.idTokenParsed;
			resolve(tokenData);
		});
	};

	updateUserData = userMetadata => {
		const tokenData = this.getTokenData();
	};

	getUserId = () => {
		return this.state.keycloak.idTokenParsed.sub;
	}

	getToken = () => {
		return this.state.keycloak.token;
	}
	
	getAdminToken = () => {
		return this.state.kcAdminClient.accessToken;
	}

	refreshToken = () => {
		setInterval(async () => {
			this.state.kcAdminClient.auth(
				credentialRadassistAdmin.credentialRadassistAdmin
			).then(()=>{
				this.state.kcAdminClient = this.state.kcAdminClient;
			});
		}, 300 * 1000);
	}

	setUserDataKeycloak = () => {

	}

	setUserData = () => {

	}

	logoutUser = () => {

	}
}

const instance = new KeycloakService();
instance.refreshToken();
export default instance;
