/**
 * Function to retrieve the CSRF token from the browser's cookies.
 * returns {string} The CSRF token if found in cookies, or an empty string if not found.
 */
function getCSRFToken() {
    const csrfCookie = document.cookie.match(/(^|;) ?csrftoken=([^;]*)(;|$)/);
    return csrfCookie ? csrfCookie[2] : '';
}


/**
 * JavaScript code to handle the click events of buttons with the 'status-button' class.
 * When a button is clicked, it updates the URL query parameter 'status' with the selected status value
 * and redirects the user to the 'audio_list' URL with the updated query parameter.
 * If 'All' is selected, it removes the 'status' query parameter.
 */
  const statusButtons = document.querySelectorAll('.status-button');

  statusButtons.forEach(button => {
    button.addEventListener('click', function() {
      const selectedStatus = this.value;

      if (selectedStatus === "All") {
        const url = new URL("{% url 'audio_list' %}", window.location.href);
        url.searchParams.delete('status');
        window.location.href = url.toString();
      } else {
        const url = new URL("{% url 'audio_list' %}", window.location.href);
        url.searchParams.set('status', selectedStatus);
        window.location.href = url.toString();
      }
    });
  });


/**
* JavaScript code for managing audio playback and transcription editing functionality.
* - Handles audio playback, including play, pause, next, and previous.
* - Manages transcription text areas and their focus.
* - Provides text manipulation features like wrapping text in angle brackets, replacing numbers with words, etc.
* - Updates playback speed and repetition factor.
* - Handles user interactions and events for audio playback.
* - Utilizes HTML elements and DOM manipulation for interaction.
* - Ensures synchronized audio and text editing.
*/

document.addEventListener('DOMContentLoaded', function() {
  const transcriptionContainers = document.querySelectorAll('.transcription-container');
  transcriptionContainers.forEach((container, index) => {
    const transcriptionText = container.querySelector('.transcription-text');
    const audioId = transcriptionText.getAttribute('data-audio-id');
    const originalTranscription = transcriptionText.value;

    // Input event listener
    transcriptionText.addEventListener('input', () => {
      if (!transcriptionText.classList.contains('edit-mode')) {
        transcriptionText.classList.add('edit-mode');
      }
      const newTranscription = transcriptionText.value;
      // Update the display and exit edit mode
      updateTranscriptionAndExitEditMode(transcriptionText, audioId, newTranscription);
    });

    // Blur event listener
    transcriptionText.addEventListener('blur', () => {
      if (transcriptionText.classList.contains('edit-mode')) {
        transcriptionText.classList.remove('edit-mode');
      }
      const newTranscription = transcriptionText.value;
      // Update the transcription and save it
      updateTranscriptionAndExitEditMode(transcriptionText, audioId, newTranscription);
    });
  });

  // Find and Replace Functionality
  const findReplaceButton = document.getElementById('findReplaceButton');
  const findInput = document.getElementById('findInput');
  const replaceInput = document.getElementById('replaceInput');

  findReplaceButton.addEventListener('click', () => {
    const findText = findInput.value;
    const replaceText = replaceInput.value;

    transcriptionContainers.forEach((container) => {
      const transcriptionText = container.querySelector('.transcription-text');
      const audioId = transcriptionText.getAttribute('data-audio-id'); // Get audioId within this loop
      const currentText = transcriptionText.value;
      const newText = currentText.replace(new RegExp(findText, 'g'), replaceText);
      transcriptionText.value = newText;

      // Update the transcription and save it
      updateTranscriptionAndExitEditMode(transcriptionText, audioId, newText);
    });
  });
});

function updateTranscriberData() {
    $.ajax({
        url: '/get_transcriber_data/', // Replace with the actual URL of your API endpoint
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            // Update the values on your page
            $('#done-duration').text(data.done_duration_formatted);
            $('#left-duration').text(data.left_duration_formatted);
            $('#total-duration').text(data.total_duration_formatted);
        },
        error: function (error) {
            console.error('Error fetching data:', error);
        }
    });
}

function updateTranscriptionAndExitEditMode(transcriptionText, audioId, newTranscription) {
  fetch(`/update_transcription/${audioId}/`, {
    method: 'POST', // Change to the appropriate HTTP method
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': getCSRFToken() // Replace with how you retrieve CSRF token
    },
    body: `newTranscription=${encodeURIComponent(newTranscription)}`
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Update the display and exit edit mode
        transcriptionText.classList.remove('edit-mode');

          updateTranscriberData();

      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

  document.addEventListener('DOMContentLoaded', () => {
    const audioList = document.querySelectorAll('.audio-list li');
    const audioElement = document.getElementById('audio-element');
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const playButton = document.getElementById('play-button');
    const pauseButton = document.getElementById('pause-button');
    const progressBar = document.getElementById('progress-bar');
    const repetitionButtons = document.querySelectorAll('.repetition-button');
    const speedButtons = document.querySelectorAll('.speed-button');
    const audioRows = document.querySelectorAll('.audio-row');
    const textareas = document.querySelectorAll('.myTextarea');

    let currentIndex = 0;
    let isPlaying = false;
    let playbackPosition = 0;
    let repetitionFactor = 1;
    let remainingRepetitions = repetitionFactor;
    let audioFocused = false;
    let audioLooping = false;
    let playbackRate = 1.0; // Initialize playback rate

    audioRows.forEach((row, index) => {
      row.addEventListener('click', () => {
        audioFocused = false;
        switchRow(index);
      });
    });

    textareas.forEach((textarea, index) => {
      textarea.addEventListener('focus', () => {
        audioFocused = false;
        switchRow(index);
        if (audioLooping) {
          playAudio(currentIndex);
        }
      });

      textarea.addEventListener('blur', () => {
        if (!audioFocused) {
          pauseAudio();
        }
      });

      textarea.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowDown') {
          event.preventDefault();
          focusNextTextarea(index);
        } else if (event.key === 'ArrowUp') {
          event.preventDefault();
          focusPreviousTextarea(index);
        } else if (event.shiftKey && event.key === 'Q') {
          event.preventDefault();
          insertTextAtCursor(textarea, '<UNCLEAR>');
        } else if (event.shiftKey && event.key === 'Z') {
          event.preventDefault();
          insertTextAtCursor(textarea, '<ah>');
        } else if (event.key === ' ') {
          event.preventDefault();
          insertTextAtCursor(textarea, ' ');
        } else if (event.key === 'Control') {
          event.preventDefault();
          wrapSelectedTextInAngleBrackets(textarea);
        } else if (event.shiftKey && event.code === 'Digit1') {
          event.preventDefault();
          replaceSelectedNumbersWithWords(textarea);
        }
      });
    });

    function wrapSelectedTextInAngleBrackets(textarea) {
      const selectionStart = textarea.selectionStart;
      const selectionEnd = textarea.selectionEnd;
      const text = textarea.value;
      const selectedText = text.substring(selectionStart, selectionEnd);
      const newText = text.substring(0, selectionStart) + '<' + selectedText + '>' + text.substring(selectionEnd);
      textarea.value = newText;
    }

    function replaceSelectedNumbersWithWords(textarea) {
      const currentValue = textarea.value;
      const selectionStart = textarea.selectionStart;
      const selectionEnd = textarea.selectionEnd;

      function replaceDigitWithWord(digit) {
        const numberToWordMap = {
          '1': 'one ',
          '2': 'two ',
          '3': 'three ',
          '4': 'four ',
          '5': 'five ',
          '6': 'six ',
          '7': 'seven ',
          '8': 'eight ',
          '9': 'nine ',
          '0': 'zero ',
        };
        return numberToWordMap[digit] || digit;
      }

      const updatedText = currentValue
        .substring(selectionStart, selectionEnd)
        .split('')
        .map(replaceDigitWithWord)
        .join('');

      const newText =
        currentValue.substring(0, selectionStart) +
        updatedText +
        currentValue.substring(selectionEnd);

      textarea.value = newText;
      textarea.setSelectionRange(
        selectionStart,
        selectionStart + updatedText.length
      );
    }

    audioElement.addEventListener('ended', () => {
      if (!audioFocused) {
        playAudio(currentIndex);
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.shiftKey && event.code === 'Space') {
        event.preventDefault();
        togglePlayPause();
      }
    });

    function playAudio(index) {
      if (isPlaying) {
        pauseAudio();
      }

      currentIndex = index;
      audioRows.forEach((row, i) => {
        row.classList.toggle('playing', i === index);
      });

      audioElement.src = audioList[index].getAttribute('data-src');
      playbackPosition = 0;
      audioElement.currentTime = playbackPosition;
      audioElement.playbackRate = playbackRate; // Set the playback rate
      audioElement.play();

      audioList.forEach((item, i) => {
        item.classList.toggle('playing', i === index);
      });

      isPlaying = true;
      playButton.style.display = 'none';
      pauseButton.style.display = 'inline';
    }

    function pauseAudio() {
      if (isPlaying) {
        audioElement.pause();
        isPlaying = false;
        playButton.style.display = 'inline';
        pauseButton.style.display = 'none';
        playbackPosition = audioElement.currentTime;
      }
    }

    function updateProgressBar() {
      const currentTime = audioElement.currentTime;
      const duration = audioElement.duration;
      const progressPercentage = (currentTime / duration) * 100;
      progressBar.style.width = `${progressPercentage}%`;
    }

    audioElement.addEventListener('ended', () => {
      if (!audioFocused) {
        playAudio(currentIndex);
      }
    });

    // Update the event listener for timeupdate
    audioElement.addEventListener('timeupdate', updateProgressBar);

    function playNext() {
      if (remainingRepetitions > 1) {
        remainingRepetitions--;
        playAudio(currentIndex);
      } else {
        currentIndex = (currentIndex + 1) % audioList.length;
        remainingRepetitions = repetitionFactor;
        playAudio(currentIndex);
      }
    }

    function playPrevious() {
      currentIndex = (currentIndex - 1 + audioList.length) % audioList.length;
      playAudio(currentIndex);
    }

    function togglePlayPause() {
      if (isPlaying) {
        pauseAudio();
      } else {
        playAudio(currentIndex);
      }
    }

    function switchRow(newIndex) {
      if (currentIndex !== newIndex) {
        if (isPlaying) {
          pauseAudio();
        }
        currentIndex = newIndex;
        playAudio(currentIndex);
        audioLooping = true;
      }
    }

    function focusNextTextarea(currentIndex) {
      audioFocused = true;
      currentIndex = (currentIndex + 1) % textareas.length;
      textareas[currentIndex].focus();
    }

    function focusPreviousTextarea(currentIndex) {
      audioFocused = true;
      currentIndex = (currentIndex - 1 + textareas.length) % textareas.length;
      textareas[currentIndex].focus();
    }

    function insertTextAtCursor(textarea, textToInsert) {
      const currentPosition = textarea.selectionStart;
      const text = textarea.value;
      const newText = text.substring(0, currentPosition) + textToInsert + text.substring(currentPosition);
      textarea.value = newText;
      const newCursorPosition = currentPosition + textToInsert.length;
      textarea.setSelectionRange(newCursorPosition, newCursorPosition);
    }

    nextButton.addEventListener('click', playNext);
    prevButton.addEventListener('click', playPrevious);

    repetitionButtons.forEach(button => {
      button.addEventListener('click', () => {
        repetitionFactor = parseInt(button.value);
        repetitionButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        remainingRepetitions = repetitionFactor;
      });
    });

    speedButtons.forEach(button => {
      button.addEventListener('click', () => {
        const newSpeed = parseFloat(button.value);
        speedButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        audioElement.playbackRate = newSpeed;
        playbackRate = newSpeed; // Store the playback rate

        // Check if audio is playing, and if so, apply the new speed immediately
        if (isPlaying) {
          audioElement.playbackRate = newSpeed;
        }
      });
    });

    playButton.addEventListener('click', () => {
      playAudio(currentIndex);
    });

    pauseButton.addEventListener('click', () => {
      pauseAudio();
    });

    playAudio(currentIndex);
    playButton.style.display = 'inline';
    pauseButton.style.display = 'none';
  });
