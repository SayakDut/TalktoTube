"""Demo data for TalkToTube when YouTube API is not accessible."""

# Sample transcript data for demonstration
DEMO_TRANSCRIPT_DATA = [
    {'text': 'Welcome to this introduction to machine learning.', 'start': 0.0, 'duration': 3.5},
    {'text': 'Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data.', 'start': 3.5, 'duration': 6.0},
    {'text': 'There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.', 'start': 9.5, 'duration': 7.0},
    {'text': 'Supervised learning uses labeled data to train models. For example, we might train a model to recognize cats in photos by showing it thousands of labeled cat and non-cat images.', 'start': 16.5, 'duration': 8.5},
    {'text': 'Unsupervised learning finds patterns in data without labels. Clustering is a common unsupervised technique that groups similar data points together.', 'start': 25.0, 'duration': 7.5},
    {'text': 'Reinforcement learning trains agents to make decisions through trial and error, receiving rewards or penalties for their actions.', 'start': 32.5, 'duration': 6.5},
    {'text': 'Popular machine learning algorithms include linear regression, decision trees, neural networks, and support vector machines.', 'start': 39.0, 'duration': 6.0},
    {'text': 'Neural networks are inspired by the human brain and consist of interconnected nodes that process information.', 'start': 45.0, 'duration': 5.5},
    {'text': 'Deep learning uses neural networks with many layers to solve complex problems like image recognition and natural language processing.', 'start': 50.5, 'duration': 7.0},
    {'text': 'Machine learning applications include recommendation systems, fraud detection, medical diagnosis, and autonomous vehicles.', 'start': 57.5, 'duration': 6.5},
    {'text': 'To get started with machine learning, you should learn programming languages like Python or R, and understand statistics and linear algebra.', 'start': 64.0, 'duration': 7.0},
    {'text': 'Popular machine learning libraries include scikit-learn, TensorFlow, and PyTorch, which provide tools for building and training models.', 'start': 71.0, 'duration': 6.5},
    {'text': 'Data preprocessing is crucial in machine learning. This includes cleaning data, handling missing values, and feature engineering.', 'start': 77.5, 'duration': 6.0},
    {'text': 'Model evaluation helps us understand how well our machine learning model performs on new, unseen data.', 'start': 83.5, 'duration': 5.5},
    {'text': 'Common evaluation metrics include accuracy, precision, recall, and F1-score for classification problems.', 'start': 89.0, 'duration': 5.0},
    {'text': 'Overfitting occurs when a model learns the training data too well and fails to generalize to new data.', 'start': 94.0, 'duration': 5.5},
    {'text': 'Cross-validation is a technique used to assess model performance and reduce overfitting by testing on multiple data splits.', 'start': 99.5, 'duration': 6.0},
    {'text': 'Feature selection helps improve model performance by identifying the most relevant input variables.', 'start': 105.5, 'duration': 5.0},
    {'text': 'Ensemble methods combine multiple models to create more robust and accurate predictions.', 'start': 110.5, 'duration': 4.5},
    {'text': 'Thank you for watching this introduction to machine learning. Keep practicing and exploring this exciting field!', 'start': 115.0, 'duration': 5.0}
]

DEMO_VIDEO_INFO = {
    'video_id': 'demo_ml_intro',
    'title': 'Introduction to Machine Learning - Demo Video',
    'channel': 'TalkToTube Demo Channel',
    'duration': '2:00',
    'url': 'https://www.youtube.com/watch?v=demo_ml_intro'
}

def get_demo_data():
    """Get demo transcript and video info."""
    return DEMO_TRANSCRIPT_DATA, DEMO_VIDEO_INFO

def is_demo_url(url: str) -> bool:
    """Check if URL is a demo URL."""
    demo_keywords = ['demo', 'test', 'sample', 'example']
    return any(keyword in url.lower() for keyword in demo_keywords)
