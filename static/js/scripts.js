window.addEventListener('load', ()=> {
  M.AutoInit();
});

window.addEventListener('load', ()=> {
  async function createDomain(reseller, domain, email) {
    let url = 'http://192.168.8.169:8085/signupdomain';
    let data = {'reseller': reseller, 'domain': domain, 'email': email}
    await axios.post(url, data)
    .catch(err => {
      errorStatus = err.response.status
      if (errorStatus == 403) {
        M.toast({html: 'Incorrect credentials'});
      }
      if (errorStatus == 500) {
        M.toast({html: 'Internal Error'});
      }
    });
  }
  submitButton = document.getElementById('submitBtn');
  submitButton.addEventListener('click', (event)=> {
    reseller = document.getElementById('reseller').value;
    domain = document.getElementById('domain').value;
    email = document.getElementById('email').value;
    createDomain(reseller, domain, email);
  });
});