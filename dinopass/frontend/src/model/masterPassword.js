import { action, thunk } from "easy-peasy";
import axios from "axios";

import { API_URL } from "../constants";
import { setCookie } from "../utils";

const MasterPassword = {
  error: "",
  loading: false,
  value: "",

  // actions
  setValue: action((state, value) => {
    state.value = value;
  }),
  setKeyDerivation: action((state, keyDerivation) => {
    state.keyDerivation = keyDerivation;
  }),
  setError: action((state, error) => {
    state.error = error;
  }),
  setLoading: action((state, loading) => {
    state.loading = loading;
  }),

  // thunks
  check: thunk(async (actions, masterPasswordPayload) => {
    actions.setError("");
    actions.setLoading(true);

    await axios
      .post(`${API_URL}/master_password/check`, masterPasswordPayload)
      .then((response) => {
        const keyDerivation = response.data.context["key_derivation"];

        actions.setLoading(false);
        setCookie("keyDerivation", keyDerivation);

        window.location.href = "/passwords";
      })
      .catch((error) => {
        actions.setError(error.response.data.detail);
        actions.setLoading(false);
      });
  }),
  create: thunk(async (actions, masterPasswordPayload) => {
    actions.setError("");
    actions.setLoading(true);

    await axios
      .post(`${API_URL}/master_password/create`, masterPasswordPayload)
      .then((response) => {
        const keyDerivation = response.data.context["key_derivation"];

        setCookie("keyDerivation", keyDerivation);
        actions.setLoading(false);
      })
      .catch((error) => {
        actions.setError(error.response.data.detail);
        actions.setLoading(false);
      });
  }),
};

export default MasterPassword;
