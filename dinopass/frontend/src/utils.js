import Cookies from 'js-cookie'
import {EXPIRE_COOKIE} from "./constants";

export const setCookie = (cookieName, cookieValue) => {
  if (!cookieValue) return null;
  if (Cookies.get(cookieName)) return null;

  Cookies.set(
    cookieName,
    cookieValue,
    {
      expires: new Date().getDate() + (EXPIRE_COOKIE * 60 * 1000),
      path: "/"
    }
  )
}

export const isAuth = () =>  !!Cookies.get('keyDerivation');
export const getKeyDerivation = () => Cookies.get('keyDerivation');