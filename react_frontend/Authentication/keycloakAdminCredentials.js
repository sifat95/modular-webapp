const credentialRadassistAdmin = {
    username: 'admin',
    password: 'admin',
    grantType: 'password',
    clientId: 'radassist-local',
};

const credentialDcm4cheAdmin = {
    username: 'admin',
    password: 'changeit',
    grantType: 'password',
    clientId: 'radassist-local',
};

// const config = process.env.NODE_ENV === 'production' ? prodConfig : devConfig;

export default { credentialDcm4cheAdmin, credentialRadassistAdmin };
