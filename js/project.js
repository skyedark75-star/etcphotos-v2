const root=document.querySelector('[data-project-root]');
const params=new URLSearchParams(location.search);
const projects=window.ETC_PROJECTS;
const project=projects.find(item=>item.slug===(params.get('id')||'a45'))||projects[0];
const projectIndex=projects.indexOf(project);
const nextProject=projects[(projectIndex+1)%projects.length];
const cover=project.coverImage;
const detail=[project.location,project.year].filter(Boolean);

document.title=`${project.title} | ETC_PHOTOS`;
document.querySelector('meta[name="description"]').content=`${project.title} automotive photography project by ETC_PHOTOS${project.location?` in ${project.location}`:''}.`;
const productionUrl=`https://etcphotos.co.uk/project.html?id=${encodeURIComponent(project.slug)}`;
const productionImage=`https://etcphotos.co.uk/${cover.src}`;
document.querySelector('link[rel="canonical"]')?.setAttribute('href',productionUrl);
document.querySelector('meta[property="og:title"]')?.setAttribute('content',`${project.title} | ETC_PHOTOS`);
document.querySelector('meta[property="og:description"]')?.setAttribute('content',`${project.title} automotive photography by ETC_PHOTOS.`);
document.querySelector('meta[property="og:url"]')?.setAttribute('content',productionUrl);
if(!document.querySelector('meta[property="og:image"]'))document.head.insertAdjacentHTML('beforeend',`<meta property="og:image" content="${productionImage}">`);

const imageSource=image=>image.src||image.full||image.original;
const previewWidth=image=>Math.min(image.width,Math.round(1100*Math.min(1,image.width/image.height))||image.width);
const responsiveImage=(image,loading='lazy')=>`<img src="${imageSource(image)}" srcset="${image.preview} ${previewWidth(image)}w, ${imageSource(image)} ${image.width}w" sizes="(max-width:850px) 100vw, 88vw" width="${image.width}" height="${image.height}" alt="${image.alt}" ${loading?`loading="${loading}"`:''} decoding="async">`;
const galleryImages=project.galleryImages;

root.innerHTML=`<section class="project-hero"><p class="eyebrow">${project.categoryLabel}${project.year?` · ${project.year}`:''}</p><div class="project-title"><h1 class="display">${project.title}</h1><a class="line-link" href="portfolio.html">All work <span>↗</span></a></div><div class="project-meta"><p><span>Project</span>${project.vehicle||project.event||project.title}</p><p><span>Category</span>${project.categoryLabel}</p>${project.location?`<p><span>Location</span>${project.location}</p>`:''}${project.year?`<p><span>Year</span>${project.year}</p>`:''}</div></section>
<section class="project-story" aria-label="${project.title} gallery">${project.description?`<p class="story-intro">${project.description}</p>`:''}<div class="project-gallery">${galleryImages.map((image,index)=>`<figure class="gallery-frame gallery-frame--${image.orientation}${index===project.coverIndex?' gallery-frame--cover':''}" style="--image-ratio:${image.aspectRatio||image.width/image.height}" tabindex="0" role="button" data-reveal data-image-index="${index}" aria-label="Open ${image.alt}">${responsiveImage(image,index===project.coverIndex?'':'lazy')}</figure>`).join('')}</div></section>
<section class="project-next"><p>Next project</p><a href="project.html?id=${nextProject.slug}">${nextProject.title} <span>↗</span></a></section>`;
window.ETC_registerReveals?.(root);

const lightbox=document.querySelector('[data-lightbox]');
const lightboxImage=lightbox.querySelector('img');
const lightboxCount=lightbox.querySelector('[data-lightbox-count]');
let activeIndex=0,lastFocus=null,touchStartX=0;

function showImage(index){activeIndex=(index+project.galleryImages.length)%project.galleryImages.length;const image=project.galleryImages[activeIndex];lightboxImage.src=imageSource(image);lightboxImage.alt=image.alt;lightboxCount.textContent=`${activeIndex+1} / ${project.galleryImages.length}`;[activeIndex-1,activeIndex+1].forEach(i=>{const preload=new Image();preload.src=imageSource(project.galleryImages[(i+project.galleryImages.length)%project.galleryImages.length])})}
function openLightbox(index,trigger){lastFocus=trigger;showImage(index);lightbox.classList.add('open');lightbox.setAttribute('aria-hidden','false');document.body.classList.add('lightbox-open');lightbox.querySelector('.lightbox-close').focus()}
function closeLightbox(){lightbox.classList.remove('open');lightbox.setAttribute('aria-hidden','true');document.body.classList.remove('lightbox-open');lastFocus?.focus()}
function handleTrigger(trigger){openLightbox(Number(trigger.dataset.imageIndex),trigger)}

document.querySelectorAll('.project-gallery-trigger,.gallery-frame').forEach(trigger=>{trigger.addEventListener('click',()=>handleTrigger(trigger));trigger.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();handleTrigger(trigger)}})});
lightbox.querySelector('.lightbox-close').addEventListener('click',closeLightbox);
lightbox.querySelector('.lightbox-prev').addEventListener('click',()=>showImage(activeIndex-1));
lightbox.querySelector('.lightbox-next').addEventListener('click',()=>showImage(activeIndex+1));
lightbox.addEventListener('click',event=>{if(event.target===lightbox)closeLightbox()});
lightbox.addEventListener('touchstart',event=>{touchStartX=event.changedTouches[0].screenX},{passive:true});
lightbox.addEventListener('touchend',event=>{const distance=touchStartX-event.changedTouches[0].screenX;if(Math.abs(distance)>50)showImage(activeIndex+(distance>0?1:-1))},{passive:true});
document.addEventListener('keydown',event=>{if(!lightbox.classList.contains('open'))return;if(event.key==='Escape')closeLightbox();if(event.key==='ArrowLeft')showImage(activeIndex-1);if(event.key==='ArrowRight')showImage(activeIndex+1)});
