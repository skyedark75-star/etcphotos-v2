const archive = document.querySelector('[data-archive]');
const archiveCount = document.querySelector('[data-archive-count]');
const filterButtons = [...document.querySelectorAll('[data-filter]')];
const previewWidth = image => Math.min(image.width, Math.round(1100 * Math.min(1, image.width / image.height)) || image.width);

const projectCard = (project, index) => {
  const cover = project.coverImage;
  const full = cover.src || cover.full;
  const detail = [project.location, project.year].filter(Boolean).join(' · ');
  return `<a class="archive-card archive-card--${cover.orientation}" href="project.html?id=${project.slug}" data-project-category="${project.category}" data-reveal>
    <figure>
      <div class="image-wrap" style="--cover-ratio:${cover.aspectRatio||cover.width/cover.height}"><img src="${cover.preview}" srcset="${cover.preview} ${previewWidth(cover)}w, ${full} ${cover.width}w" sizes="(max-width:850px) 100vw, 68vw" width="${cover.width}" height="${cover.height}" alt="${cover.alt}" ${index ? 'loading="lazy"' : ''} decoding="async"></div>
      <figcaption class="archive-meta"><div><p>${String(index+1).padStart(2,'0')} · ${project.categoryLabel}</p><h2>${project.title}</h2><span>View project ↗</span></div>${detail?`<p>${detail}</p>`:''}</figcaption>
    </figure>
  </a>`;
};

function renderArchive(filter = 'all') {
  const projects = window.ETC_PROJECTS.filter(project => filter === 'all' || project.category === filter);
  archive.innerHTML = projects.map(projectCard).join('');
  archiveCount.textContent = `${projects.length} ${projects.length === 1 ? 'project' : 'projects'}`;
  filterButtons.forEach(button => {
    const active = button.dataset.filter === filter;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  window.ETC_registerReveals?.(archive);
}

filterButtons.forEach(button => button.addEventListener('click', () => renderArchive(button.dataset.filter)));
renderArchive();
