import {action, thunk} from "easy-peasy";
import axios from "axios";

const masterPassword = {
  error: '',
  keyDerivation: '',
  loading: false,
  value: '',

  // actions
  setValue: action((state, value) => {
    state.value = value
  }),
  setKeyDerivation: action((state, keyDerivation) => {
    state.keyDerivation = keyDerivation
  }),
  setError: action((state, error) => {
    state.error = error
  }),
  setLoading: action((state, loading) => {
    state.loading = loading
  }),

  // thunks
  check: thunk(async (actions, masterPasswordPayload) => {
    actions.setError('');
    actions.setLoading(true);

    await axios.post('http://localhost:8888/api/master_password/check', masterPasswordPayload)
      .then(response => {
        const keyDerivation = response.data.context["key_derivation"]

        actions.setKeyDerivation(keyDerivation)
        actions.setLoading(false);
      })
      .catch(error => {
        actions.setError(error.response.data.detail)
        actions.setLoading(false);
      })
  }),
  create: thunk(async (actions, masterPasswordPayload) => {
    actions.setError('');
    actions.setLoading(true);

    await axios.post('http://localhost:8888/api/master_password/create', masterPasswordPayload)
      .then(response => {
        const keyDerivation = response.data.context["key_derivation"]

        actions.setKeyDerivation(keyDerivation)
        actions.setLoading(false);
      })
      .catch(error => {
        actions.setError(error.response.data.detail)
        actions.setLoading(false);
      })
  }),
}

export default masterPassword;