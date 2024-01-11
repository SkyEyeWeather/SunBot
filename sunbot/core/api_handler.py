"""API Handler"""

import logging
from typing import Dict, List, Literal, Optional, Union

import requests

from sunbot.utils.utils import flatten_dict, get_best_items, merge_dict

AuthMode = Literal["no", "token", "jwt"]
AuthModes = AuthMode.__args__


class APIHandler:
    """The APIHandler class defines an object able to call a web API
    and to handle corresponding response from this API. This class supports many
    authentification methods, namely no authentification, token authentification (default)
    and JWT. This handler can manage HTML, JSON and XML response's content

    Parameters
    ----------

    :param domain_name : web API domain name. ex: github.com
    :type domain_name: str
    :param auth_mode : str, optional
        Authentification mode:
            - no: no authentification system is required to access to web API
            - token (default): a access token is requred to use the API. Then, the
                user have to provide a valid token key in `auth_args` dict paramater.
                Key name for token must follow the name expected by web API in the
                URL. See web API documentation to see what name is expected.
                Ex: auth_agrs={'token': my_token}
            - jwt: this authentification mod generates time-limited token used to
                access to web API. This class handles the update of a token when it
                expires. Data needed to create a jeton have to be passed into the
                `auth_args` parameter
                Ex: auth_args= {'token_url': my_token_url, 'app_id': my_app_id}
    :param

    """

    ACCEPTED_FORMATS = ["application/json"]
    DEFAULT_ACCEPTED_FORMAT = {_format: 1.0 for _format in ACCEPTED_FORMATS}

    def __init__(
        self,
        domain_name: str,
        auth_mode: Optional[AuthMode] = "token",
        accepted_formats: Union[Dict[str, float], None] = None,
        **kwargs,
    ) -> None:
        """_summary_

        Parameters
        ----------
        domain_name : str
            API domain name, for instance www.visualcrossing.com
        auth_mode : Optional[AuthMode], optional
            API authentification method , by default "token"
        accepted_formats : Union[Dict[str, float], None], optional
            dict of accepted format, with key representing format and value
            the associated priority (a weight of 1.0 indicates that corresponding
            format has a higher priority, than one with a weight of 0.8). This
            priority is used by HTTP for format resolution. The default value
            is None, so DEFAULT_ACCEPTED_FORMAT will be used (application/json,
            with a priority of 1.0)

        Raises
        ------
        NotImplementedError
            For now application/json format is the only format supported by the bot.
        """
        # Create a session to maintains connection with the web API and speed
        # up the reception of a response from the API
        self.session = requests.Session()

        # For now, this handler only accept JSON format response from web API:
        # See https://http.dev/accept for more info about Accept HTTP header
        accepted_formats = (
            accepted_formats
            if accepted_formats is not None
            else self.DEFAULT_ACCEPTED_FORMAT
        )
        accepted_formats_str = ""
        for _format, priority in accepted_formats.items():
            if _format not in self.ACCEPTED_FORMATS:
                logging.warning("%s is not supported for now", _format)
                continue
            accepted_formats_str += _format + ";q=" + str(priority) + ","
        if len(accepted_formats_str) == 0:
            raise NotImplementedError(
                "All the specified accepted format are not supported for now"
            )
        self.session.headers.update({"Accept": accepted_formats_str[:-1]})

        self.domain_name = domain_name
        self.certificate_file = kwargs.get("certificate_file")
        auth_mode_id = AuthModes.index("token")
        try:
            auth_mode_id = AuthModes.index(auth_mode)
        # If authentification mode is not recognized
        except ValueError:
            logging.warning(
                "specified authentification mode (%s) was not recognized.\
                            Possible values for this argument are: %s. Set to no.",
                auth_mode,
                AuthModes,
            )
        finally:
            self.auth_mode = auth_mode_id
        # Token authentification mode only need a token
        if self.auth_mode == AuthModes.index("token"):
            self.auth_args = kwargs.get("auth_args", {})
            if self.auth_args is None:
                logging.warning(
                    "Token authentification need a token, but no one was provided."
                )
        # JWT authentification mode need an application id and a token url
        if self.auth_mode == AuthModes.index("jwt"):
            self.auth_args = kwargs.get("auth_args", {})
            for missing_key in {"token_url", "app_id"} - {self.auth_args}:
                logging.warning(
                    "JWT authentification mode needs %s but no one was provided",
                    missing_key,
                )

    def __build_url(
        self,
        resource_path: str,
        url_args: Dict[str, str] | None = None,
        protocol: str = "https",
    ) -> str:
        """Build a request URL

        Parameters
        ----------
        resource_path: str
            path to the reosurce on the web API
        url_args: Dict[str, str]
            parameters used for the URL, as key:value dict
        protocol:
            protocol used for the communication between the bot and the web API

        Returns
        -------
            built URL
        """
        if protocol != "https":
            raise NotImplementedError("APIHandler only supports HTTPS protcol")
        # Add a '/' to separate domain name from resource path
        if resource_path[0] != "/" and self.domain_name[-1] != "/":
            resource_path = "/" + resource_path
        url = protocol + "://" + self.domain_name + resource_path

        # If authentification mode is token, add the web API token to URL arguments:
        if self.auth_mode == AuthModes.index("token"):
            url_args = merge_dict(url_args, self.auth_args)

        # Add URL parameters
        if url_args is not None:
            url += "?"
            for key, value in url_args.items():
                url += f"{key}={value}&"
            url = url[:-1]
        return url

    @staticmethod
    def __token_has_expired(response: requests.Response) -> bool:
        """Check wether authentification token has expired

        Parameters
        ----------
        response : requests.Response
            response received from an API

        Returns
        -------
        bool
            `True` if authentification token has expired, else `False`
        """
        status = response.status_code
        return status == 401 and "expired" in response.headers["WWW-Authenticate"]

    def __obtain_jwt_token(self, timeout: Optional[float] = 10.0) -> bool:
        """Obtain new jwt token from the web API. The token is added into
        session's header

        Parameters
        ----------
        timeout : float, optional
            maximum waiting time between the sending of the token generation request
            and the response from web API. Default to 10 seconds

        Returns
        ------
        boolean indicating whether jwt token was correctly set for current session
        or not.
        """
        logging.info("Requesting a new JWT for %s web API", self.domain_name)
        data = {"grant_type": "client_credentials"}
        headers = {"Authorization": f'Basic {self.auth_args["app_id"]}'}
        access_token_response = requests.post(
            self.auth_args["token_url"],
            data=data,
            verify=self.certificate_file,
            allow_redirects=True,
            headers=headers,
            timeout=timeout,
        )
        if access_token_response.status_code == requests.Response:
            token = access_token_response.json()["access_token"]
            # Update session with fresh token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            logging.info("JWT successfully updated for %s web API", self.domain_name)
            return True
        logging.error(
            "An error occured when getting a JWT for %s web API. Code error: %d",
            self.domain_name,
            access_token_response.status_code,
        )
        return False

    def request(
        self,
        resource_path: str,
        request_args: Dict[str, str] | None = None,
        protocol: str = "https",
        method: Literal["GET", "POST"] = "GET",
    ) -> requests.Response:
        """Send a request to the web API

        Parameters
        ----------
        resource_path : str
            path to the resource on the web API
        request_args : Dict[str, str]
            parameters used for the request URL, as key=value dict
        protocol : str
            protocol used for the request. Default to HTTPS
        method : str
            request method

        Return
        ------
            request response : requests.Response object
        """
        # First request will always need to obtain a token first, when using JWT auth
        # mode
        if (
            "Authorization" not in self.session.headers
            and self.auth_mode == AuthModes.index("jwt")
        ):
            self.__obtain_jwt_token()
        # Generate request URL
        url = self.__build_url(resource_path, request_args, protocol)
        # send request to web API:
        response = self.session.request(method, url)
        if self.__token_has_expired(response):
            # Update token:
            self.__obtain_jwt_token()
            response = self.session.request(method, url)
        return response

    @staticmethod
    def get_data(
        response: requests.Response,
        targets: Union[str, List[str], Dict[str, str]],
        tolerance: Optional[float] = 0.0,
        verbose: Optional[bool] = False,
    ) -> Dict[str, any]:
        """Get data from the specified request response and format it following
        the structure indicated in `data_keys`

        Parameters
        ----------
        :param response: response from the web API for a request
        :type response: requests.Response
        :param targets: list of keys to search in response structure. It is
        also possible to specified a dict where keys are target to search in response and
        value are corresponding keys in the dict returned by this method.
        :type data_keys: List[str]
        :param tolerance: tolerance to apply on search results
        :type tolerance: Optional[float]
        :param verbose:
        :type verbose: Optional[bool]

        Returns
        -------
        :returns: formatted dictionnary
        :rtype: dict

        Raises
        -----

        :raise NotImplementedError: if response data is not provided as JSON format
        """
        data = {}
        content_type = response.headers["Content-Type"]
        # only JSON format is supported for now:
        if "application/json" not in content_type:
            raise NotImplementedError(
                f"The API handler does not support {content_type} formats"
            )
        json_resp = response.json()
        # flatten json response
        flattened_json_resp = flatten_dict(json_resp)

        if isinstance(targets, str):
            targets_list = [targets]
        elif isinstance(targets, dict):
            targets_list = targets.keys()
        else:
            targets_list = targets

        for target in targets_list:
            filtered_dict = get_best_items(
                flattened_json_resp, target=target, tolerance=tolerance, verbose=verbose
            )
            key = targets[target] if isinstance(targets, dict) else target
            # if filtered dict contains only one item, use its unique value instead
            if len(filtered_dict) == 1:
                data[key] = filtered_dict[list(filtered_dict)[0]]
            else:
                data[key] = filtered_dict
        return data
