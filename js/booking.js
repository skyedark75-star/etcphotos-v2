const packageOptions = [...document.querySelectorAll('[data-package]')];
const enquiryForm = document.querySelector('[data-enquiry-form]');
const summaryPackage = document.querySelector('[data-summary-package]');
const summaryDuration = document.querySelector('[data-summary-duration]');
const summaryPrice = document.querySelector('[data-summary-price]');
let selectedPackage = null;

function renderPackageSelection() {
  packageOptions.forEach(option => {
    const selected = option === selectedPackage;
    option.classList.toggle('selected', selected);
    option.setAttribute('aria-pressed', String(selected));
    option.querySelector('.choice-dot').textContent = selected ? '✓' : '+';
  });

  summaryPackage.textContent = selectedPackage?.dataset.package || 'No package selected';
  summaryDuration.textContent = selectedPackage?.dataset.duration || '—';
  summaryPrice.textContent = selectedPackage ? `£${selectedPackage.dataset.price}` : '—';
}

packageOptions.forEach(option => option.addEventListener('click', () => {
  selectedPackage = option;
  renderPackageSelection();
}));

enquiryForm.addEventListener('submit', event => {
  event.preventDefault();
  if (!selectedPackage) {
    summaryPackage.textContent = 'Select a package first';
    packageOptions[0].focus();
    return;
  }

  const details = new FormData(enquiryForm);
  const subject = encodeURIComponent(`Photography enquiry — ${selectedPackage.dataset.package}`);
  const message = encodeURIComponent([
    'Hi ETC_PHOTOS,',
    '',
    `I'd like to enquire about a ${selectedPackage.dataset.package} automotive photography session.`,
    '',
    `Name: ${details.get('name')}`,
    `Email: ${details.get('email')}`,
    `Vehicle: ${details.get('vehicle')}`,
    `Preferred date/timeframe: ${details.get('date') || 'To discuss'}`,
    `Package: ${selectedPackage.dataset.package}`,
    `Duration: ${selectedPackage.dataset.duration}`,
    `Price: £${selectedPackage.dataset.price}`,
    '',
    `Notes: ${details.get('message') || 'None'}`,
    '',
    'I understand location and travel will be discussed before the booking is confirmed.',
    '',
    'Thanks,'
  ].join('\n'));

  window.location.href = `mailto:contact@etcphotos.co.uk?subject=${subject}&body=${message}`;
});

renderPackageSelection();
