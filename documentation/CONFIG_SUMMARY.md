# MIA System Configuration Summary

## Current Configuration

### LLM Models

#### Gemini (Vision Analysis)
- **Model**: `gemini-2.5-flash` ✅ **UPDATED**
- **Purpose**: MRI image vision analysis and cross-validation
- **Temperature**: 0.1 (low for consistency)
- **Max Tokens**: 8,192
- **Safety**: All categories set to BLOCK_NONE for medical content

#### Groq (Report Generation)
- **Model**: `llama-3.3-70b-versatile`
- **Purpose**: Medical report generation and safety analysis
- **Temperature**: 0.2 (low for consistency)
- **Max Tokens**: 8,000

### API Keys Required

Set in `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### Model Capabilities

**Gemini 2.5 Flash**:
- ✅ Vision capabilities (can analyze images)
- ✅ Fast response times
- ✅ High accuracy for medical imaging
- ✅ Stable release (not experimental)
- ✅ Better rate limits than experimental versions

**Groq Llama 3.3 70B**:
- ✅ Excellent text generation
- ✅ Medical knowledge
- ✅ Fast inference
- ✅ Structured output support

### Why Gemini 2.5 Flash?

1. **Stable Release**: Not experimental, more reliable
2. **Vision Support**: Can analyze MRI images
3. **Medical Accuracy**: Excellent for medical image analysis
4. **Speed**: Fast response times
5. **Cost-Effective**: Good balance of performance and cost

### Configuration File

All settings in: `config.py`

To change models, edit:
```python
GEMINI_CONFIG = {
    "model_name": "gemini-2.5-flash",  # Change here
    # ...
}

GROQ_CONFIG = {
    "model_name": "llama-3.3-70b-versatile",  # Or here
    # ...
}
```

### Testing Configuration

Test Gemini connection:
```bash
.miavenv\Scripts\python.exe -c "from services import get_gemini_service; s = get_gemini_service(); print('✅ Gemini connected')"
```

Test Groq connection:
```bash
.miavenv\Scripts\python.exe -c "from services import get_groq_service; s = get_groq_service(); print('✅ Groq connected')"
```

### Rate Limits

**Gemini 2.5 Flash (Free Tier)**:
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per minute

**Groq (Free Tier)**:
- Varies by model
- Generally higher than Gemini
- Check Groq dashboard for current limits

### Recommended Settings

For production use:
```python
GEMINI_CONFIG = {
    "model_name": "gemini-2.5-flash",
    "temperature": 0.1,  # Consistent results
    "max_output_tokens": 8192,
}

GROQ_CONFIG = {
    "model_name": "llama-3.3-70b-versatile",
    "temperature": 0.2,  # Slightly higher for creativity
    "max_output_tokens": 8000,
}
```

### Alternative Models

If you need to switch:

**Gemini Alternatives**:
- `gemini-1.5-flash` - Previous version
- `gemini-1.5-pro` - More capable but slower
- `gemini-2.0-flash-exp` - Experimental, may have issues

**Groq Alternatives**:
- `llama-3.1-70b-versatile` - Previous version
- `mixtral-8x7b-32768` - Different architecture
- `gemma-7b-it` - Smaller, faster

### Current Status

✅ **Gemini**: Configured with stable 2.5 Flash model  
✅ **Groq**: Configured with Llama 3.3 70B  
✅ **API Keys**: Set in .env file  
✅ **Safety Settings**: Configured for medical content  
✅ **Ready**: System ready to use  
