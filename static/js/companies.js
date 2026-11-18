document.querySelectorAll('.bookmark-btn').forEach(button=>{
  button.addEventListener('click',()=>{
    button.classList.toggle('saved');
    button.textContent=button.classList.contains('saved')?'♥':'♡';
  });
});
