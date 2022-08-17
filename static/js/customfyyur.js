
const deleteBtn = document.getElementById('delete-venue');
deleteBtn.onclick = function(e) {
  const venueId = e.target.dataset.id;
  fetch('/venues/'+ venueId ,{
    method: 'DELETE'
  })
  .then((response) => {
    if (response.ok){
      // If venue was successfully deleted, take the user back to the links of venues page
      window.location.href = '/venues';
    }
    throw new Error('Could not delete venue')
  })
  .catch((e) => {
    // if error occurs we want to redirect the user back to the venue specif page
    window.location.href = '/venues/' + venueId;
  });
};

