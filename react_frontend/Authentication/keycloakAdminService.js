import KcAdminClient from 'keycloak-admin';
import credentialDcm4cheAdmin from './keycloakAdminCredentials';

// To configure the client, pass an object to override any of these  options:
const config = {
  baseUrl: 'https://dev.radassist.net/auth',
  realmName: 'dcm4che',
}
const kcAdminClientDcm4che = new KcAdminClient(config);

// Authorize with username / password
kcAdminClientDcm4che.auth(
  credentialDcm4cheAdmin.credentialDcm4cheAdmin
);

setInterval(async () => {
  kcAdminClientDcm4che.auth(
    credentialDcm4cheAdmin.credentialDcm4cheAdmin
  );
}, 300 * 1000); // 58 seconds

export default kcAdminClientDcm4che;