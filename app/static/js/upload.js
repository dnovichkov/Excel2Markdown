/**
 * File upload handling for Excel2Markdown
 */
(function() {
    'use strict';

    var dropZone = document.getElementById('drop-zone');
    var fileInput = document.getElementById('file-input');
    var fileInfo = document.getElementById('file-info');
    var fileName = document.getElementById('file-name');
    var fileRemove = document.getElementById('file-remove');
    var submitBtn = document.getElementById('submit-btn');
    var form = document.getElementById('upload-form');

    if (!dropZone || !fileInput) return;

    // Allowed extensions
    var allowedExtensions = ['.xls', '.xlsx'];

    // Click to upload
    dropZone.addEventListener('click', function() {
        fileInput.click();
    });

    // Drag and drop events
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');

        var files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });

    // Remove file
    fileRemove.addEventListener('click', function(e) {
        e.stopPropagation();
        clearFile();
    });

    // Handle selected file
    function handleFile(file) {
        // Validate extension
        var ext = '.' + file.name.split('.').pop().toLowerCase();
        if (allowedExtensions.indexOf(ext) === -1) {
            alert('Invalid file type. Please upload an Excel file (.xls or .xlsx)');
            return;
        }

        // Update UI
        fileName.textContent = file.name;
        dropZone.querySelector('.drop-zone-content').style.display = 'none';
        fileInfo.style.display = 'flex';
        submitBtn.disabled = false;

        // Set file to input
        var dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;
    }

    // Clear file selection
    function clearFile() {
        fileInput.value = '';
        dropZone.querySelector('.drop-zone-content').style.display = 'block';
        fileInfo.style.display = 'none';
        submitBtn.disabled = true;
    }

    // Form submission
    form.addEventListener('submit', function() {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Uploading...';
    });
})();
