// Import the necessary function from the installed package
import { YoutubeTranscript } from 'youtube-transcript';

// Get the video ID from the command-line arguments
const videoId = process.argv[2];

if (!videoId) {
  console.error('Error: No video ID provided.');
  process.exit(1);
}

// Define the main function to fetch the transcript
async function getTranscript(id) {
  try {
    // Fetch the transcript using the library
    const transcript = await YoutubeTranscript.fetchTranscript(id);

    // If successful, print the result as a JSON string to standard output
    // This is how Python will receive the data
    console.log(JSON.stringify(transcript, null, 2));

  } catch (error) {
    // If there's an error, print it to standard error and exit
    // This tells Python that the script failed
    console.error(`Error fetching transcript for ${id}:`, error.message);
    process.exit(1);
  }
}

// Run the function
getTranscript(videoId);