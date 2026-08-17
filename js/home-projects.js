const featured = window.ETC_PROJECTS.filter(project => project.featured).sort((a,b) => a.featured - b.featured);
const featuredGrid = document.querySelector('[data-featured-projects]');
const featuredStatement = document.querySelector('[data-featured-statement]');
const previewWidth = image => Math.min(image.width, Math.round(1100 * Math.min(1, image.width / image.height)) || image.width);

featuredGrid.innerHTML = featured.slice(0,2).map((project,index) => {
  const cover = project.coverImage;
  const full = cover.src || cover.full;
  return `<a class="work-card ${index?'small':''}" href="project.html?id=${project.slug}" data-reveal>
    <figure><div class="image-wrap"><img src="${cover.preview}" srcset="${cover.preview} ${previewWidth(cover)}w, ${full} ${cover.width}w" sizes="(max-width:850px) 100vw, ${index?'38vw':'62vw'}" width="${cover.width}" height="${cover.height}" alt="${cover.alt}" loading="lazy" decoding="async"></div>
    <figcaption class="card-meta"><span>${String(index+1).padStart(2,'0')} · ${project.categoryLabel}</span><small>${[project.location,project.year].filter(Boolean).join(' · ')}</small><h3>${project.title}</h3></figcaption></figure>
  </a>`;
}).join('');

const statementProject = featured[2] || featured[0];
if (statementProject) {
  const cover = statementProject.coverImage;
  const full = cover.src || cover.full;
  featuredStatement.innerHTML = `<img src="${full}" srcset="${cover.preview} ${previewWidth(cover)}w, ${full} ${cover.width}w" sizes="100vw" width="${cover.width}" height="${cover.height}" alt="${cover.alt}" loading="lazy" data-parallax><div data-reveal><p class="eyebrow">Form · Detail · Atmosphere</p><h2>More than<br>a record.</h2><a class="button" href="project.html?id=${statementProject.slug}">View ${statementProject.title} <span>↗</span></a></div>`;
}

[featuredGrid,featuredStatement].forEach(container => window.ETC_registerReveals?.(container));
