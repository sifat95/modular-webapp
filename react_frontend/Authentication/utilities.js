import jwt_decode from 'jwt-decode';
import instance from '../src/app/services/keycloakService';
import kcAdminClientDcm4che from '../src/app/services/keycloakService/keycloakAdminService';

let API_BASE_URL = 'http://localhost:5000';
const ACCESS_TOKEN_KEY = 'accessToken';

const validateAccessToken = () => {
  try {
    const dateobj = new Date();
    const time = Math.floor(dateobj.getTime() / 1000);
    const jwtdata = parseInt(jwt_decode(getAccessToken()).exp);
    if (jwtdata < time) {
      clearLocalStorage();
      return false;
    }
    return true;
  } catch (err) {
    clearLocalStorage();
    return false;
  }
};

const _flattenArray = a => {
  return a.flat(10);
};

const _flattenObject = o => {
  let errors = [];
  Object.values(o).forEach(value => {
    if (Array.isArray(value)) errors.push(..._flattenArray(value));
    else if (typeof value === 'object') errors.push(..._flattenObject(value));
    else errors.push(value);
  });
  return errors;
};

const flattenErrorMessages = response => {
  console.log(response);
  const errorMessage = response.response.response.data.error.msg;

  if (typeof errorMessage === 'string') {
    return [errorMessage];
  }

  if (typeof errorMessage === 'object') {
    let errors = [];
    Object.values(errorMessage).forEach(value => {
      if (Array.isArray(value)) errors.push(..._flattenArray(value));
      else if (typeof value === 'object') errors.push(..._flattenObject(value));
      else errors.push(value);
    });
    return errors.length > 0 ? [errors[0]] : [];
  }
};

const formatDate = dateTime => {
  return (
    dateTime.getDate() +
    '/' +
    (dateTime.getMonth() + 1) +
    '/' +
    dateTime.getFullYear()
  );
};

const setAccessToken = accessToken => {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
};

const getAccessToken = () => instance.getAdminToken();

const getAccessTokenDcm4che = () => kcAdminClientDcm4che.accessToken;

const logout = () =>
  instance.state.keycloak.logout({ redirectUri: 'http://localhost:3000/' });

const getUserId = () => instance.getUserId();

const clearLocalStorage = () => localStorage.clear();

export {
  validateAccessToken,
  getAccessToken,
  getAccessTokenDcm4che,
  setAccessToken,
  clearLocalStorage,
  flattenErrorMessages,
  formatDate,
  getUserId,
  logout,
  API_BASE_URL,
};