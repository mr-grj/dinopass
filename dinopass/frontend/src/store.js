import {createStore, action, thunk} from 'easy-peasy';

import axios from "axios";


export const store = createStore({
  masterPassword: '',
  masterPasswordLoading: false,
  keyDerivation: '',
  errorMessage: '',

  // actions
  setMasterPassword: action((state, masterPassword) => {
    state.masterPassword = masterPassword
  }),
  setKeyDerivation: action((state, keyDerivation) => {
    state.keyDerivation = keyDerivation
  }),
  setErrorMessage: action((state, errorMessage) => {
    state.errorMessage = errorMessage
  }),
  setMasterPasswordLoading: action((state, masterPasswordLoading) => {
    state.masterPasswordLoading = masterPasswordLoading
  }),

  // thunks
  checkMasterPassword: thunk(async (actions, masterPasswordPayload) => {
    actions.setErrorMessage('');
    actions.setMasterPasswordLoading(true);

    await axios.post('http://localhost:8888/api/master_password/check', masterPasswordPayload)
      .then(response => {
        const keyDerivation = response.data.context["key_derivation"]

        actions.setKeyDerivation(keyDerivation)
        actions.setMasterPasswordLoading(false);
      })
      .catch(error => {
        actions.setErrorMessage(error.response.data.detail)
        actions.setMasterPasswordLoading(false);
      })
  }),
  createMasterPassword: thunk(async (actions, masterPasswordPayload) => {
    actions.setErrorMessage('');
    actions.setMasterPasswordLoading(true);

    await axios.post('http://localhost:8888/api/master_password/create', masterPasswordPayload)
      .then(response => {
        const keyDerivation = response.data.context["key_derivation"]

        actions.setKeyDerivation(keyDerivation)
        actions.setMasterPasswordLoading(false);
      })
      .catch(error => {
        actions.setErrorMessage(error.response.data.detail)
        actions.setMasterPasswordLoading(false);
      })
  }),
});