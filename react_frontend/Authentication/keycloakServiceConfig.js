const prodConfig = {
    "realm": "dcm4che",
    "auth-server-url": "https://34.121.99.7:8843/auth/",
    "ssl-required": "external",
    "resource": "radassist",
    "public-client": true,
    "confidential-port": 0
};

const devConfig = {
    "realm": "dcm4che",
    "auth-server-url": "https://34.121.99.7:8843/auth/",
    "ssl-required": "external",
    "resource": "radassist",
    "public-client": true,
    "confidential-port": 0
};

const config = process.env.NODE_ENV === 'production' ? prodConfig : devConfig;

export default config;
