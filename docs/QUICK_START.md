# Quick Start - Document Processing

## ✅ Ready to Use

The document processing API is fully functional and ready for frontend integration.

---

## 📌 Quick Commands

### Test Non-Streaming
```bash
curl -X POST http://localhost:8002/process-document/ \
  -F "file=@your_document.md" \
  -F "style_preset=ecommerce_entrepreneur"
```

### Test Streaming (with progress)
```bash
curl -N -X POST http://localhost:8002/process-document-stream/ \
  -F "file=@your_document.md" \
  -F "style_preset=ecommerce_entrepreneur"
```

---

## 📋 Supported Formats

- ✅ `.txt` - Plain text
- ✅ `.md` - Markdown  
- ✅ `.docx` - Microsoft Word
- ✅ `.pdf` - PDF (text-based only)

---

## 🎨 Available Styles

- `ecommerce_entrepreneur` - Roman Urdu, for Shopify/DTC brands
- `professional_business` - English, corporate tone
- `social_media_casual` - English, casual
- `educational_content` - English, informative
- `fitness_wellness` - English, motivational

---

## 📚 Documentation

1. **API Guide** → `api_guide.md` (Complete reference)
2. **Summary** → `DOCUMENT_SUPPORT_SUMMARY.md` (Feature overview)
3. **Swagger** → http://localhost:8002/docs (Interactive docs)

---

## 🚀 Frontend Integration Example

```javascript
// Upload and process document with progress
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('style_preset', 'ecommerce_entrepreneur');
formData.append('force_regenerate', false);

// Option 1: Non-streaming (simple)
const response = await fetch('http://localhost:8002/process-document/', {
  method: 'POST',
  body: formData
});
const result = await response.json();
console.log(result.content_pieces); // Array of generated content

// Option 2: Streaming (with progress)
const eventSource = new EventSource('http://localhost:8002/process-document-stream/');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}% - ${data.message}`);
  
  if (data.status === 'complete') {
    console.log('Done!', data.data);
    eventSource.close();
  }
};
```

---

## ✨ What You Get

For each document, the API generates **6-8 content pieces**:

1. **Reels** - Video scripts with hooks, captions, visual suggestions
2. **Image Carousels** - Multi-slide posts (4-6 slides each)
3. **Tweets** - Social media posts with hashtags

All content includes:
- ✅ Titles
- ✅ Captions  
- ✅ Hashtags
- ✅ CTAs (calls-to-action)
- ✅ Visual suggestions (for reels/carousels)

---

## ⏱️ Expected Performance

- **Upload & Parse**: < 1 second
- **Ideas Generation**: ~20 seconds
- **Content Creation**: ~70 seconds
- **Total**: ~90 seconds per document

---

## 🔗 Test It Now!

```bash
# Create a test file
echo "E-commerce in Pakistan is booming with 100M+ users!" > test.txt

# Process it
curl -X POST http://localhost:8002/process-document/ \
  -F "file=@test.txt" \
  -F "style_preset=ecommerce_entrepreneur"
```

---

**Status**: ✅ Production Ready  
**Server**: http://localhost:8002  
**Last Updated**: November 15, 2024
