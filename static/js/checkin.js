document.addEventListener('DOMContentLoaded', () => {
	const entryEl = document.getElementById('entry');
	const validNames = new Set(window.names);
	const validCards = new Set(window.cards.map(c => c.toLowerCase()));
	const autoData = {};
	window.names.forEach(n => autoData[n] = null);
  
	M.Autocomplete.init(entryEl, {
	  data: autoData,
	  minLength: 1,
	  limit: 8
	});
  
	setTimeout(() => {
	  entryEl.focus();
	  entryEl.select();
	}, 300);
  });
  