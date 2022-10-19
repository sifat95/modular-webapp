import axios from 'axios';
import QueryString from 'query-string';
import { getAccessToken, getUserId, API_BASE_URL } from './utilities';

const getAccessToken = async callback => {
  const url =
    'https://dev.radassist.net/auth/realms/radassist/protocol/openid-connect/token';
  let apiResponse = { response: null, error: false, msg: '' };

  let data = axios({
    method: 'POST',
    url: url,
    data: QueryString.stringify({
      grant_type: 'password',
      username: 'admin',
      password: 'admin',
      client_id: 'radassist-local',
    }),
    contentType: 'application/x-www-form-urlencoded',
  });

  return data;
};

const apiResponse = apiResponse => {
  const statusCode = apiResponse.response.status;

  if (statusCode === 200) {
    return apiResponse.response.data.access_token;
  } else {
    console.log('Failed while retrieving data from api');
  }
};

const getUserAttributes = async callback => {
  // let respond = await get_Access_Token(apiResponsefromradassist);
  const url = API_BASE_URL + `/get-user-profile/${getUserId()}`;
  let apiResponse = { response: null, error: false, msg: '' };
  axios({
    method: 'GET',
    url: url,
    headers: {
      Authorization: 'Bearer ' + getAccessToken(),
    },
    responseType: 'json',
    responseEncoding: 'utf8',
  })
    .then(response => {
      apiResponse.response = response;
    })
    .catch(error => {
      apiResponse.response = error;
      apiResponse.error = true;
    })
    .finally(() => {
      callback(apiResponse);
    });
};

export {
  getUserAttributes,
};

export var API_BASE_URL_LOCAL = API_BASE_URL;