import {action, thunk} from "easy-peasy";
import axios from "axios";

import {API_URL} from "../constants";


const Passwords = {
  error: '',
  loading: false,
  passwords: [],

  // actions
  setError: action((state, error) => {
    state.error = error
  }),
  setLoading: action((state, loading) => {
    state.loading = loading
  }),
  setPasswords: action((state, passwords) => {
    state.passwords = passwords
  }),

  // thunks
  get: thunk( async (actions, keyDerivation) => {
    actions.setLoading(true);
    await axios.get(`${API_URL}/passwords/${keyDerivation}`)
      .then(response => {
        actions.setPasswords(response.data.passwords)
        actions.setLoading(false)
      })
      .catch(error => {
        actions.setError(error.response.data.detail)
        actions.setLoading(false)
      })
  })
}

export default Passwords;