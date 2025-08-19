function copyText(element) {
  const textarea = document.createElement("textarea");
  textarea.value = element.innerText;
  document.body.appendChild(textarea);
  textarea.select();
  // textarea.setSelectionRange(0, 99999); // For mobile devices
  document.execCommand("copy");
  document.body.removeChild(textarea);

  showCopyNotification(element);
}

function showCopyNotification(element) {
  const svgIcon = element.querySelector('svg');
  const originalUseHref = svgIcon.querySelector('use').getAttribute('href');
  
  // Change icon to checkmark
  svgIcon.querySelector('use').setAttribute('href', '#icon-check');
  svgIcon.style.color = '#16a34a'; // green-600
  
  // Create and show notification bubble
  const notification = document.createElement('div');
  notification.className = 'copy-notification';
  notification.textContent = 'Skopiowane!';
  
  // Position relative to the element
  element.style.position = 'relative';
  element.appendChild(notification);
  
  // Restore original icon and remove notification after 3 seconds
  setTimeout(() => {
    svgIcon.querySelector('use').setAttribute('href', originalUseHref);
    svgIcon.style.color = '';
    if (notification.parentNode) {
      notification.remove();
    }
  }, 3000);
}

function handleCopyKeydown(event, element) {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    copyText(element);
  }
}

function isInAppBrowser() {
  const ua = navigator.userAgent || navigator.vendor || window.opera;
  return (ua.indexOf('Instagram') > -1) || 
         (ua.indexOf('FBAN') > -1) || 
         (ua.indexOf('FBAV') > -1) ||
         (ua.indexOf('Twitter') > -1) ||
         (ua.indexOf('Line/') > -1);
}

function forceExternalBrowser(url) {
  if (isInAppBrowser()) {
    const intent = `intent://${url.replace(/^https?:\/\//, '')}#Intent;scheme=https;action=android.intent.action.VIEW;category=android.intent.category.BROWSABLE;package=com.android.chrome;end`;
    const fallback = url;
    
    if (/Android/i.test(navigator.userAgent)) {
      window.location.href = intent;
      setTimeout(() => {
        window.location.href = fallback;
      }, 500);
    } else if (/iPhone|iPad/i.test(navigator.userAgent)) {
      window.location.href = `x-web-search://?url=${encodeURIComponent(url)}`;
      setTimeout(() => {
        window.location.href = url;
      }, 500);
    } else {
      window.open(url, '_blank');
    }
    return true;
  }
  return false;
}

function showInAppBrowserBanner() {
  const banner = document.createElement('div');
  banner.className = 'in-app-browser-banner';
  banner.innerHTML = `
    <div class="banner-content-container">
      <div class="banner-icon-container">
        <svg class="banner-warning-icon" fill="currentColor">
          <use href="#icon-warning"></use>
        </svg>
      </div>
      <div class="banner-text-container">
        <p class="banner-text">
          <strong>Otwórz w przeglądarce</strong> - Aby uzyskać najlepsze doświadczenie, zalecamy otwarcie tej strony w zewnętrznej przeglądarce.
        </p>
      </div>
      <div class="banner-button-container">
        <svg class="banner-external-icon" fill="none" stroke="currentColor" stroke-width="2">
          <use href="#icon-external-link"></use>
        </svg>
      </div>
    </div>
  `;
  
  banner.addEventListener('click', function() {
    forceExternalBrowser(window.location.href);
  });
  
  const nav = document.querySelector('nav');
  nav.insertAdjacentElement('afterend', banner);
}

function shareCurrentPage() {
  // Check if Web Share API is available and we're on HTTPS (required for mobile)
  if (navigator.share && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    navigator.share({
      title: document.title,
      url: window.location.href
    }).catch(err => {
      console.log('Share failed:', err);
      // Fallback if share fails
      copyUrlFallback(window.location.href);
    });
  } else {
    // For HTTP or browsers without Web Share API
    const url = window.location.href;
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(url).then(() => {
        alert('Link skopiowany do schowka!');
      }).catch(() => {
        copyUrlFallback(url);
      });
    } else {
      copyUrlFallback(url);
    }
  }
}

function copyUrlFallback(url) {
  const textarea = document.createElement('textarea');
  textarea.value = url;
  document.body.appendChild(textarea);
  textarea.select();
  try {
    document.execCommand('copy');
    alert('Link skopiowany do schowka!');
  } catch (err) {
    alert('Link: ' + url);
  }
  document.body.removeChild(textarea);
}

document.addEventListener('DOMContentLoaded', function() {
  if (isInAppBrowser()) {
    // Show banner for in-app browsers
    showInAppBrowserBanner();
    
    // Handle external links
    document.querySelectorAll('a[href^="http"]').forEach(function(link) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        forceExternalBrowser(this.href);
      });
    });
  }
});
