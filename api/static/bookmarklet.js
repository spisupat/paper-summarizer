(function() {
    // Get the HTML content
    const htmlContent = document.documentElement.outerHTML;
    const pageUrl = document.location.href;
    const pageTitle = document.title;
    
    // Create a modal to show progress
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.7)';
    modal.style.zIndex = '999999';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    
    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '20px';
    modalContent.style.borderRadius = '5px';
    modalContent.style.maxWidth = '500px';
    modalContent.style.width = '80%';
    modalContent.innerHTML = '<h3>Summarizing page...</h3><p>Please wait while we generate your summary.</p>';
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Send to our API
    fetch('/api/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            html: htmlContent,
            url: pageUrl,
            title: pageTitle
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.summary) {
            // Copy to clipboard on client side (backup in case server-side didn't work)
            copyToClipboard(data.summary);
            
            // Show success message
            modalContent.innerHTML = '<h3>Summary copied to clipboard!</h3>';
            
            // Add preview button
            const previewButton = document.createElement('button');
            previewButton.textContent = 'Preview Summary';
            previewButton.style.padding = '8px 16px';
            previewButton.style.marginTop = '10px';
            previewButton.style.backgroundColor = '#4CAF50';
            previewButton.style.color = 'white';
            previewButton.style.border = 'none';
            previewButton.style.borderRadius = '4px';
            previewButton.style.cursor = 'pointer';
            previewButton.style.marginRight = '10px';
            previewButton.onclick = function() {
                modalContent.innerHTML = '<h3>Summary</h3><div style="max-height: 60vh; overflow-y: auto; white-space: pre-wrap;">' + data.summary + '</div>';
                
                // Add close button
                const closeButton = document.createElement('button');
                closeButton.textContent = 'Close';
                closeButton.style.padding = '8px 16px';
                closeButton.style.marginTop = '10px';
                closeButton.style.backgroundColor = '#f44336';
                closeButton.style.color = 'white';
                closeButton.style.border = 'none';
                closeButton.style.borderRadius = '4px';
                closeButton.style.cursor = 'pointer';
                closeButton.onclick = function() {
                    document.body.removeChild(modal);
                };
                modalContent.appendChild(closeButton);
            };
            modalContent.appendChild(previewButton);
            
            // Add close button
            const closeButton = document.createElement('button');
            closeButton.textContent = 'Close';
            closeButton.style.padding = '8px 16px';
            closeButton.style.marginTop = '10px';
            closeButton.style.backgroundColor = '#f44336';
            closeButton.style.color = 'white';
            closeButton.style.border = 'none';
            closeButton.style.borderRadius = '4px';
            closeButton.style.cursor = 'pointer';
            closeButton.onclick = function() {
                document.body.removeChild(modal);
            };
            modalContent.appendChild(closeButton);
        } else {
            modalContent.innerHTML = '<h3>Error</h3><p>' + (data.error || 'Failed to generate summary') + '</p>';
            
            // Add close button
            const closeButton = document.createElement('button');
            closeButton.textContent = 'Close';
            closeButton.style.padding = '8px 16px';
            closeButton.style.marginTop = '10px';
            closeButton.style.backgroundColor = '#f44336';
            closeButton.style.color = 'white';
            closeButton.style.border = 'none';
            closeButton.style.borderRadius = '4px';
            closeButton.style.cursor = 'pointer';
            closeButton.onclick = function() {
                document.body.removeChild(modal);
            };
            modalContent.appendChild(closeButton);
        }
    })
    .catch(error => {
        modalContent.innerHTML = '<h3>Error</h3><p>Network error: ' + error.message + '</p>';
        
        // Add close button
        const closeButton = document.createElement('button');
        closeButton.textContent = 'Close';
        closeButton.style.padding = '8px 16px';
        closeButton.style.marginTop = '10px';
        closeButton.style.backgroundColor = '#f44336';
        closeButton.style.color = 'white';
        closeButton.style.border = 'none';
        closeButton.style.borderRadius = '4px';
        closeButton.style.cursor = 'pointer';
        closeButton.onclick = function() {
            document.body.removeChild(modal);
        };
        modalContent.appendChild(closeButton);
    });
    
    // Helper function to copy text to clipboard
    function copyToClipboard(text) {
        // Create a temporary element
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'absolute';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        
        // Select and copy the text
        textarea.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Failed to copy text to clipboard:', err);
        }
        
        // Clean up
        document.body.removeChild(textarea);
    }
})(); 