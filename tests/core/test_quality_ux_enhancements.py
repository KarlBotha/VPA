#!/usr/bin/env python3
"""
VPA Quality & UX Enhancements Testing Suite

This comprehensive testing suite validates the Quality & UX Enhancements milestone
implementation, ensuring all quality analysis, feedback processing, and user experience
improvements work correctly.

Usage:
    python tests/core/test_quality_ux_enhancements.py
    python -m pytest tests/core/test_quality_ux_enhancements.py -v
    python -m pytest tests/core/test_quality_ux_enhancements.py --cov=src.vpa.core
"""

import asyncio
import json
import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import sys
import os
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.vpa.core.quality_ux_enhancements import (
        VPAQualityAnalyzer,
        VPAFeedbackProcessor,
        VPAUXEnhancer,
        QualityMetrics,
        UserFeedback,
        UXEnhancementConfig,
        ResponseQuality,
        UserSatisfactionLevel,
        FeedbackType,
        create_enhanced_vpa_system
    )
    VPA_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: VPA imports not available: {e}")
    VPA_IMPORTS_AVAILABLE = False


class TestQualityMetrics(unittest.TestCase):
    """Test quality metrics functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quality_metrics = QualityMetrics()
    
    def test_quality_metrics_initialization(self):
        """Test QualityMetrics initialization."""
        self.assertEqual(self.quality_metrics.relevance_score, 0.0)
        self.assertEqual(self.quality_metrics.accuracy_score, 0.0)
        self.assertEqual(self.quality_metrics.completeness_score, 0.0)
        self.assertEqual(self.quality_metrics.clarity_score, 0.0)
        self.assertEqual(self.quality_metrics.helpfulness_score, 0.0)
        self.assertEqual(self.quality_metrics.overall_quality, ResponseQuality.AVERAGE)
    
    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        # Set all scores to 0.8
        self.quality_metrics.relevance_score = 0.8
        self.quality_metrics.accuracy_score = 0.8
        self.quality_metrics.completeness_score = 0.8
        self.quality_metrics.clarity_score = 0.8
        self.quality_metrics.helpfulness_score = 0.8
        
        overall_score = self.quality_metrics.calculate_overall_score()
        self.assertEqual(overall_score, 0.8)
    
    def test_calculate_overall_score_mixed_values(self):
        """Test overall score calculation with mixed values."""
        self.quality_metrics.relevance_score = 1.0
        self.quality_metrics.accuracy_score = 0.6
        self.quality_metrics.completeness_score = 0.8
        self.quality_metrics.clarity_score = 0.7
        self.quality_metrics.helpfulness_score = 0.9
        
        overall_score = self.quality_metrics.calculate_overall_score()
        expected_score = (1.0 + 0.6 + 0.8 + 0.7 + 0.9) / 5
        self.assertEqual(overall_score, expected_score)
    
    def test_calculate_overall_score_empty_scores(self):
        """Test overall score calculation with empty scores."""
        overall_score = self.quality_metrics.calculate_overall_score()
        self.assertEqual(overall_score, 0.0)


class TestUserFeedback(unittest.TestCase):
    """Test user feedback functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.feedback = UserFeedback(
            user_id="test_user",
            session_id="test_session",
            response_id="test_response",
            feedback_type=FeedbackType.QUALITY_RATING,
            rating=5
        )
    
    def test_user_feedback_initialization(self):
        """Test UserFeedback initialization."""
        self.assertEqual(self.feedback.user_id, "test_user")
        self.assertEqual(self.feedback.session_id, "test_session")
        self.assertEqual(self.feedback.response_id, "test_response")
        self.assertEqual(self.feedback.feedback_type, FeedbackType.QUALITY_RATING)
        self.assertEqual(self.feedback.rating, 5)
        self.assertIsNotNone(self.feedback.feedback_id)
        self.assertIsInstance(self.feedback.timestamp, datetime)
    
    def test_feedback_to_dict(self):
        """Test feedback conversion to dictionary."""
        feedback_dict = self.feedback.to_dict()
        
        self.assertIn("feedback_id", feedback_dict)
        self.assertIn("user_id", feedback_dict)
        self.assertIn("session_id", feedback_dict)
        self.assertIn("response_id", feedback_dict)
        self.assertIn("feedback_type", feedback_dict)
        self.assertIn("rating", feedback_dict)
        self.assertIn("timestamp", feedback_dict)
        
        self.assertEqual(feedback_dict["user_id"], "test_user")
        self.assertEqual(feedback_dict["rating"], 5)
        self.assertEqual(feedback_dict["feedback_type"], "quality_rating")
    
    def test_feedback_types(self):
        """Test different feedback types."""
        # Quality rating
        quality_feedback = UserFeedback(
            feedback_type=FeedbackType.QUALITY_RATING,
            rating=4
        )
        self.assertEqual(quality_feedback.feedback_type, FeedbackType.QUALITY_RATING)
        
        # Thumbs up/down
        thumbs_feedback = UserFeedback(
            feedback_type=FeedbackType.THUMBS_UP_DOWN,
            thumbs_up=True
        )
        self.assertEqual(thumbs_feedback.feedback_type, FeedbackType.THUMBS_UP_DOWN)
        self.assertTrue(thumbs_feedback.thumbs_up)
        
        # Detailed feedback
        detailed_feedback = UserFeedback(
            feedback_type=FeedbackType.DETAILED_FEEDBACK,
            detailed_feedback="Great response, very helpful!"
        )
        self.assertEqual(detailed_feedback.feedback_type, FeedbackType.DETAILED_FEEDBACK)
        self.assertEqual(detailed_feedback.detailed_feedback, "Great response, very helpful!")


@unittest.skipIf(not VPA_IMPORTS_AVAILABLE, "VPA imports not available")
class TestVPAQualityAnalyzer(unittest.TestCase):
    """Test VPA quality analyzer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = UXEnhancementConfig()
        self.analyzer = VPAQualityAnalyzer(self.config)
    
    def test_quality_analyzer_initialization(self):
        """Test quality analyzer initialization."""
        self.assertIsInstance(self.analyzer, VPAQualityAnalyzer)
        self.assertEqual(self.analyzer.config, self.config)
        self.assertIsInstance(self.analyzer.quality_history, dict)
        self.assertIsInstance(self.analyzer.performance_cache, dict)
    
    async def test_analyze_response_quality(self):
        """Test response quality analysis."""
        response_content = "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data."
        user_query = "What is machine learning?"
        
        metrics = await self.analyzer.analyze_response_quality(
            response_content=response_content,
            user_query=user_query,
            response_time=1.5
        )
        
        self.assertIsInstance(metrics, QualityMetrics)
        self.assertEqual(metrics.response_time, 1.5)
        self.assertGreater(metrics.relevance_score, 0.0)
        self.assertGreater(metrics.accuracy_score, 0.0)
        self.assertGreater(metrics.completeness_score, 0.0)
        self.assertGreater(metrics.clarity_score, 0.0)
        self.assertGreater(metrics.helpfulness_score, 0.0)
        self.assertIsInstance(metrics.overall_quality, ResponseQuality)
    
    async def test_analyze_relevance(self):
        """Test relevance analysis."""
        response = "Python is a programming language used for machine learning and data science."
        query = "What is Python programming?"
        
        relevance_score = await self.analyzer._analyze_relevance(response, query)
        
        self.assertIsInstance(relevance_score, float)
        self.assertGreaterEqual(relevance_score, 0.0)
        self.assertLessEqual(relevance_score, 1.0)
        self.assertGreater(relevance_score, 0.5)  # Should be highly relevant
    
    async def test_analyze_accuracy(self):
        """Test accuracy analysis."""
        response = "Python is definitely a programming language that was created by Guido van Rossum."
        context = "Python programming language history and features"
        
        accuracy_score = await self.analyzer._analyze_accuracy(response, context)
        
        self.assertIsInstance(accuracy_score, float)
        self.assertGreaterEqual(accuracy_score, 0.0)
        self.assertLessEqual(accuracy_score, 1.0)
    
    async def test_analyze_completeness(self):
        """Test completeness analysis."""
        response = """Python is a high-level programming language. First, it's easy to learn and use. 
        Second, it has extensive libraries. Third, it's great for data science. Finally, it has 
        a large community. For example, you can use NumPy for numerical computing."""
        query = "Tell me about Python programming language"
        
        completeness_score = await self.analyzer._analyze_completeness(response, query)
        
        self.assertIsInstance(completeness_score, float)
        self.assertGreaterEqual(completeness_score, 0.0)
        self.assertLessEqual(completeness_score, 1.0)
        self.assertGreater(completeness_score, 0.5)  # Should be fairly complete
    
    async def test_analyze_clarity(self):
        """Test clarity analysis."""
        response = "Python is easy to learn. It has simple syntax. You can use it for many tasks."
        
        clarity_score = await self.analyzer._analyze_clarity(response)
        
        self.assertIsInstance(clarity_score, float)
        self.assertGreaterEqual(clarity_score, 0.0)
        self.assertLessEqual(clarity_score, 1.0)
        self.assertGreater(clarity_score, 0.5)  # Should be clear and simple
    
    async def test_analyze_helpfulness(self):
        """Test helpfulness analysis."""
        response = """You should try Python for beginners. I recommend starting with basic syntax. 
        Consider using online tutorials. Specifically, focus on variables and functions."""
        query = "How to learn Python?"
        
        helpfulness_score = await self.analyzer._analyze_helpfulness(response, query)
        
        self.assertIsInstance(helpfulness_score, float)
        self.assertGreaterEqual(helpfulness_score, 0.0)
        self.assertLessEqual(helpfulness_score, 1.0)
        self.assertGreater(helpfulness_score, 0.5)  # Should be helpful with actionable advice
    
    async def test_calculate_token_efficiency(self):
        """Test token efficiency calculation."""
        response = "Python programming language artificial intelligence machine learning data science"
        
        efficiency = await self.analyzer._calculate_token_efficiency(response)
        
        self.assertIsInstance(efficiency, float)
        self.assertGreaterEqual(efficiency, 0.0)
        self.assertLessEqual(efficiency, 1.0)
    
    async def test_calculate_context_utilization(self):
        """Test context utilization calculation."""
        response = "Based on the provided context, Python is widely used for data science and machine learning applications."
        context = "Python programming language data science machine learning applications"
        
        utilization = await self.analyzer._calculate_context_utilization(response, context)
        
        self.assertIsInstance(utilization, float)
        self.assertGreaterEqual(utilization, 0.0)
        self.assertLessEqual(utilization, 1.0)
        self.assertGreater(utilization, 0.3)  # Should show good context utilization
    
    def test_determine_quality_level(self):
        """Test quality level determination."""
        # Test excellent quality
        excellent_score = 0.95
        quality = self.analyzer._determine_quality_level(excellent_score)
        self.assertEqual(quality, ResponseQuality.EXCELLENT)
        
        # Test good quality
        good_score = 0.75
        quality = self.analyzer._determine_quality_level(good_score)
        self.assertEqual(quality, ResponseQuality.GOOD)
        
        # Test average quality
        average_score = 0.55
        quality = self.analyzer._determine_quality_level(average_score)
        self.assertEqual(quality, ResponseQuality.AVERAGE)
        
        # Test poor quality
        poor_score = 0.35
        quality = self.analyzer._determine_quality_level(poor_score)
        self.assertEqual(quality, ResponseQuality.POOR)
        
        # Test unacceptable quality
        unacceptable_score = 0.1
        quality = self.analyzer._determine_quality_level(unacceptable_score)
        self.assertEqual(quality, ResponseQuality.UNACCEPTABLE)
    
    async def test_get_quality_trends(self):
        """Test quality trends retrieval."""
        trends = await self.analyzer.get_quality_trends(days=7)
        
        self.assertIsInstance(trends, dict)
        self.assertIn("overall_quality_trend", trends)
        self.assertIn("response_time_trend", trends)
        self.assertIn("user_satisfaction_trend", trends)
        self.assertIn("quality_by_provider", trends)
        self.assertIn("improvement_areas", trends)


@unittest.skipIf(not VPA_IMPORTS_AVAILABLE, "VPA imports not available")
class TestVPAFeedbackProcessor(unittest.TestCase):
    """Test VPA feedback processor functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = UXEnhancementConfig()
        self.processor = VPAFeedbackProcessor(self.config)
    
    def test_feedback_processor_initialization(self):
        """Test feedback processor initialization."""
        self.assertIsInstance(self.processor, VPAFeedbackProcessor)
        self.assertEqual(self.processor.config, self.config)
        self.assertEqual(len(self.processor.feedback_queue), 0)
        self.assertEqual(len(self.processor.feedback_history), 0)
    
    async def test_collect_feedback(self):
        """Test feedback collection."""
        feedback = UserFeedback(
            user_id="test_user",
            feedback_type=FeedbackType.QUALITY_RATING,
            rating=5
        )
        
        result = await self.processor.collect_feedback(feedback)
        
        self.assertTrue(result)
        self.assertEqual(len(self.processor.feedback_queue), 1)
        self.assertEqual(len(self.processor.feedback_history), 1)
        self.assertEqual(self.processor.feedback_history[0], feedback)
    
    async def test_collect_critical_feedback(self):
        """Test critical feedback collection."""
        critical_feedback = UserFeedback(
            user_id="test_user",
            feedback_type=FeedbackType.BUG_REPORT,
            detailed_feedback="System crashed when processing query"
        )
        
        result = await self.processor.collect_feedback(critical_feedback)
        
        self.assertTrue(result)
        self.assertEqual(len(self.processor.feedback_queue), 1)
        self.assertEqual(len(self.processor.improvement_actions), 1)
        
        # Check that urgent action was created
        action = self.processor.improvement_actions[0]
        self.assertEqual(action["priority"], "critical")
        self.assertEqual(action["action"], "urgent_investigation")
    
    async def test_process_feedback_batch(self):
        """Test feedback batch processing."""
        # Add multiple feedback items
        feedbacks = [
            UserFeedback(user_id="user1", feedback_type=FeedbackType.QUALITY_RATING, rating=5),
            UserFeedback(user_id="user2", feedback_type=FeedbackType.QUALITY_RATING, rating=2),
            UserFeedback(user_id="user3", feedback_type=FeedbackType.THUMBS_UP_DOWN, thumbs_up=True),
            UserFeedback(user_id="user4", feedback_type=FeedbackType.THUMBS_UP_DOWN, thumbs_up=False),
            UserFeedback(user_id="user5", feedback_type=FeedbackType.DETAILED_FEEDBACK, detailed_feedback="Great quality response!")
        ]
        
        for feedback in feedbacks:
            await self.processor.collect_feedback(feedback)
        
        # Process batch
        result = await self.processor.process_feedback_batch()
        
        self.assertIsInstance(result, dict)
        self.assertIn("processed", result)
        self.assertIn("insights", result)
        self.assertIn("improvement_actions", result)
        self.assertEqual(result["processed"], 5)
        self.assertEqual(len(result["insights"]), 5)
        self.assertGreater(len(result["improvement_actions"]), 0)
    
    async def test_analyze_feedback_quality_rating(self):
        """Test feedback analysis for quality rating."""
        # High rating feedback
        high_rating_feedback = UserFeedback(
            feedback_type=FeedbackType.QUALITY_RATING,
            rating=5
        )
        
        insight = await self.processor._analyze_feedback(high_rating_feedback)
        
        self.assertIsNotNone(insight)
        self.assertEqual(insight["sentiment"], "positive")
        self.assertEqual(insight["severity"], "low")
        
        # Low rating feedback
        low_rating_feedback = UserFeedback(
            feedback_type=FeedbackType.QUALITY_RATING,
            rating=1
        )
        
        insight = await self.processor._analyze_feedback(low_rating_feedback)
        
        self.assertIsNotNone(insight)
        self.assertEqual(insight["sentiment"], "negative")
        self.assertEqual(insight["severity"], "high")
        self.assertTrue(insight["actionable"])
    
    async def test_analyze_feedback_thumbs(self):
        """Test feedback analysis for thumbs up/down."""
        # Thumbs up feedback
        thumbs_up_feedback = UserFeedback(
            feedback_type=FeedbackType.THUMBS_UP_DOWN,
            thumbs_up=True
        )
        
        insight = await self.processor._analyze_feedback(thumbs_up_feedback)
        
        self.assertIsNotNone(insight)
        self.assertEqual(insight["sentiment"], "positive")
        self.assertEqual(insight["severity"], "low")
        
        # Thumbs down feedback
        thumbs_down_feedback = UserFeedback(
            feedback_type=FeedbackType.THUMBS_UP_DOWN,
            thumbs_up=False
        )
        
        insight = await self.processor._analyze_feedback(thumbs_down_feedback)
        
        self.assertIsNotNone(insight)
        self.assertEqual(insight["sentiment"], "negative")
        self.assertEqual(insight["severity"], "medium")
        self.assertTrue(insight["actionable"])
    
    async def test_extract_themes(self):
        """Test theme extraction from feedback text."""
        feedback_text = "The response quality was poor and the UI interface was confusing. The system was also slow to respond."
        
        themes = await self.processor._extract_themes(feedback_text)
        
        self.assertIsInstance(themes, list)
        self.assertIn("response_quality", themes)
        self.assertIn("response_speed", themes)
        self.assertIn("user_interface", themes)
    
    async def test_generate_improvement_actions(self):
        """Test improvement action generation."""
        insights = [
            {"sentiment": "negative", "severity": "high", "themes": ["response_quality"]},
            {"sentiment": "negative", "severity": "high", "themes": ["response_quality"]},
            {"sentiment": "negative", "severity": "medium", "themes": ["user_interface"]},
            {"sentiment": "negative", "severity": "medium", "themes": ["user_interface"]},
            {"sentiment": "negative", "severity": "medium", "themes": ["user_interface"]},
            {"sentiment": "negative", "severity": "medium", "themes": ["user_interface"]}
        ]
        
        actions = await self.processor._generate_improvement_actions(insights)
        
        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)
        
        # Check for high severity action
        high_severity_actions = [a for a in actions if a["priority"] == "critical"]
        self.assertGreater(len(high_severity_actions), 0)
        
        # Check for theme-based action
        theme_actions = [a for a in actions if a["action"] == "address_user_interface"]
        self.assertGreater(len(theme_actions), 0)
    
    async def test_get_feedback_analytics(self):
        """Test feedback analytics."""
        # Add sample feedback
        feedbacks = [
            UserFeedback(feedback_type=FeedbackType.QUALITY_RATING, rating=5),
            UserFeedback(feedback_type=FeedbackType.QUALITY_RATING, rating=4),
            UserFeedback(feedback_type=FeedbackType.QUALITY_RATING, rating=3),
            UserFeedback(feedback_type=FeedbackType.THUMBS_UP_DOWN, thumbs_up=True),
            UserFeedback(feedback_type=FeedbackType.THUMBS_UP_DOWN, thumbs_up=False)
        ]
        
        self.processor.feedback_history = feedbacks
        
        analytics = await self.processor.get_feedback_analytics(days=30)
        
        self.assertIsInstance(analytics, dict)
        self.assertIn("total_feedback", analytics)
        self.assertIn("feedback_by_type", analytics)
        self.assertIn("average_rating", analytics)
        self.assertIn("satisfaction_rate", analytics)
        
        self.assertEqual(analytics["total_feedback"], 5)
        self.assertEqual(analytics["average_rating"], 4.0)  # (5+4+3)/3
        self.assertEqual(analytics["satisfaction_rate"], 0.5)  # 1 thumbs up, 1 thumbs down


@unittest.skipIf(not VPA_IMPORTS_AVAILABLE, "VPA imports not available")
class TestVPAUXEnhancer(unittest.TestCase):
    """Test VPA UX enhancer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = UXEnhancementConfig()
        self.enhancer = VPAUXEnhancer(self.config)
    
    def test_ux_enhancer_initialization(self):
        """Test UX enhancer initialization."""
        self.assertIsInstance(self.enhancer, VPAUXEnhancer)
        self.assertEqual(self.enhancer.config, self.config)
        self.assertIsInstance(self.enhancer.quality_analyzer, VPAQualityAnalyzer)
        self.assertIsInstance(self.enhancer.feedback_processor, VPAFeedbackProcessor)
    
    async def test_enhance_response(self):
        """Test response enhancement."""
        response_content = "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed."
        user_query = "What is machine learning?"
        user_id = "test_user"
        session_id = "test_session"
        
        enhanced_response = await self.enhancer.enhance_response(
            response_content=response_content,
            user_query=user_query,
            user_id=user_id,
            session_id=session_id
        )
        
        self.assertIsInstance(enhanced_response, dict)
        self.assertIn("content", enhanced_response)
        self.assertIn("quality_metrics", enhanced_response)
        self.assertIn("user_id", enhanced_response)
        self.assertIn("session_id", enhanced_response)
        self.assertIn("response_id", enhanced_response)
        self.assertIn("enhancements", enhanced_response)
        
        self.assertEqual(enhanced_response["content"], response_content)
        self.assertEqual(enhanced_response["user_id"], user_id)
        self.assertEqual(enhanced_response["session_id"], session_id)
        
        # Check enhancements
        enhancements = enhanced_response["enhancements"]
        self.assertIn("suggestion_chips", enhancements)
        self.assertIn("contextual_help", enhancements)
        self.assertIn("formatting_improvements", enhancements)
        self.assertIn("accessibility_features", enhancements)
    
    async def test_generate_suggestion_chips(self):
        """Test suggestion chip generation."""
        query = "What is machine learning?"
        response = "Machine learning is a subset of artificial intelligence that focuses on neural networks and deep learning algorithms."
        
        suggestions = await self.enhancer._generate_suggestion_chips(query, response)
        
        self.assertIsInstance(suggestions, list)
        self.assertLessEqual(len(suggestions), 5)  # Should be limited to 5
        
        # Check for machine learning related suggestions
        ml_suggestions = [s for s in suggestions if "neural network" in s["text"].lower()]
        self.assertGreater(len(ml_suggestions), 0)
        
        # Check suggestion structure
        for suggestion in suggestions:
            self.assertIn("text", suggestion)
            self.assertIn("action", suggestion)
            self.assertIn("priority", suggestion)
            self.assertIn(suggestion["action"], ["query", "rephrase", "example"])
            self.assertIn(suggestion["priority"], ["high", "medium", "low"])
    
    async def test_generate_contextual_help(self):
        """Test contextual help generation."""
        query = "How to implement machine learning?"
        response = "Machine learning implementation involves several steps including data preparation, model selection, training, and evaluation."
        
        help_tips = await self.enhancer._generate_contextual_help(query, response)
        
        self.assertIsInstance(help_tips, list)
        
        # Check for "how to" related tips
        how_to_tips = [tip for tip in help_tips if "step" in tip["content"].lower()]
        self.assertGreater(len(how_to_tips), 0)
        
        # Check tip structure
        for tip in help_tips:
            self.assertIn("type", tip)
            self.assertIn("title", tip)
            self.assertIn("content", tip)
            self.assertEqual(tip["type"], "tip")
    
    async def test_improve_formatting(self):
        """Test formatting improvements."""
        response = """Here's how to use Python:
        1. Install Python
        2. Write your code
        3. Run the script
        
        ```python
        print("Hello, World!")
        ```
        
        Important: Always use proper indentation."""
        
        improvements = await self.enhancer._improve_formatting(response)
        
        self.assertIsInstance(improvements, dict)
        self.assertIn("structured_format", improvements)
        self.assertIn("highlights", improvements)
        self.assertIn("code_blocks", improvements)
        self.assertIn("bullet_points", improvements)
        
        # Should detect code blocks
        self.assertGreater(len(improvements["code_blocks"]), 0)
        
        # Should detect bullet points
        self.assertGreater(len(improvements["bullet_points"]), 0)
        
        # Should detect highlights
        self.assertIn("important", improvements["highlights"])
    
    async def test_add_accessibility_features(self):
        """Test accessibility feature addition."""
        response = "This is a comprehensive explanation of machine learning concepts with detailed examples and practical applications."
        
        features = await self.enhancer._add_accessibility_features(response)
        
        self.assertIsInstance(features, dict)
        self.assertIn("alt_text", features)
        self.assertIn("reading_time", features)
        self.assertIn("complexity_level", features)
        self.assertIn("screen_reader_friendly", features)
        
        # Check reading time calculation
        self.assertGreater(features["reading_time"], 0)
        
        # Check complexity level
        self.assertIn(features["complexity_level"], ["low", "medium", "high"])
        
        # Check screen reader compatibility
        self.assertIsInstance(features["screen_reader_friendly"], bool)
    
    async def test_update_session_analytics(self):
        """Test session analytics update."""
        session_id = "test_session"
        quality_metrics = QualityMetrics()
        quality_metrics.relevance_score = 0.8
        quality_metrics.accuracy_score = 0.9
        quality_metrics.completeness_score = 0.7
        quality_metrics.clarity_score = 0.8
        quality_metrics.helpfulness_score = 0.85
        
        await self.enhancer._update_session_analytics(session_id, quality_metrics)
        
        self.assertIn(session_id, self.enhancer.session_analytics)
        session_data = self.enhancer.session_analytics[session_id]
        
        self.assertIn("start_time", session_data)
        self.assertIn("response_count", session_data)
        self.assertIn("quality_scores", session_data)
        self.assertIn("average_quality", session_data)
        
        self.assertEqual(session_data["response_count"], 1)
        self.assertEqual(len(session_data["quality_scores"]), 1)
        self.assertGreater(session_data["average_quality"], 0.7)
    
    async def test_get_user_analytics(self):
        """Test user analytics retrieval."""
        user_id = "test_user"
        
        # Add mock session data
        self.enhancer.session_analytics["session1"] = {
            "user_id": user_id,
            "response_count": 5,
            "quality_scores": [0.8, 0.9, 0.7, 0.85, 0.75],
            "average_quality": 0.8
        }
        
        self.enhancer.session_analytics["session2"] = {
            "user_id": user_id,
            "response_count": 3,
            "quality_scores": [0.7, 0.8, 0.9],
            "average_quality": 0.8
        }
        
        analytics = await self.enhancer.get_user_analytics(user_id)
        
        self.assertIsInstance(analytics, dict)
        self.assertIn("user_id", analytics)
        self.assertIn("total_sessions", analytics)
        self.assertIn("total_responses", analytics)
        self.assertIn("average_quality", analytics)
        self.assertIn("recommendations", analytics)
        
        self.assertEqual(analytics["user_id"], user_id)
        self.assertEqual(analytics["total_sessions"], 2)
        self.assertEqual(analytics["total_responses"], 8)
        self.assertGreater(analytics["average_quality"], 0.7)
    
    async def test_implement_improvement_action(self):
        """Test improvement action implementation."""
        # Test quality improvement action
        quality_action = {
            "action": "improve_response_quality",
            "priority": "high",
            "description": "Multiple negative feedback items detected"
        }
        
        await self.enhancer._implement_improvement_action(quality_action)
        
        # Check that quality thresholds were adjusted
        original_thresholds = VPAQualityAnalyzer(self.config).quality_thresholds
        adjusted_thresholds = self.enhancer.quality_analyzer.quality_thresholds
        
        for quality, threshold in adjusted_thresholds.items():
            self.assertGreaterEqual(threshold, original_thresholds[quality])
        
        # Test urgent review action
        urgent_action = {
            "action": "urgent_quality_review",
            "priority": "critical",
            "description": "High severity issues detected"
        }
        
        with self.assertLogs(level='WARNING') as log:
            await self.enhancer._implement_improvement_action(urgent_action)
            self.assertIn("Urgent quality review needed", log.output[0])
        
        # Test theme-based action
        theme_action = {
            "action": "address_user_interface",
            "priority": "medium",
            "description": "Multiple feedback items about user_interface"
        }
        
        with self.assertLogs(level='INFO') as log:
            await self.enhancer._implement_improvement_action(theme_action)
            self.assertIn("Addressing theme: user_interface", log.output[0])


@unittest.skipIf(not VPA_IMPORTS_AVAILABLE, "VPA imports not available")
class TestUXEnhancementConfig(unittest.TestCase):
    """Test UX enhancement configuration."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        config = UXEnhancementConfig()
        
        self.assertTrue(config.enable_response_streaming)
        self.assertTrue(config.enable_typing_indicators)
        self.assertTrue(config.enable_suggestion_chips)
        self.assertTrue(config.enable_contextual_help)
        self.assertTrue(config.enable_personalization)
        self.assertTrue(config.enable_accessibility_features)
        self.assertEqual(config.response_quality_threshold, 0.7)
        self.assertEqual(config.user_satisfaction_threshold, 0.8)
        self.assertEqual(config.feedback_processing_interval, 300)
        self.assertTrue(config.quality_analysis_enabled)
        self.assertTrue(config.real_time_improvements)
    
    def test_config_customization(self):
        """Test configuration customization."""
        config = UXEnhancementConfig(
            enable_response_streaming=False,
            enable_suggestion_chips=False,
            response_quality_threshold=0.8,
            user_satisfaction_threshold=0.9,
            feedback_processing_interval=600,
            quality_analysis_enabled=False,
            real_time_improvements=False
        )
        
        self.assertFalse(config.enable_response_streaming)
        self.assertFalse(config.enable_suggestion_chips)
        self.assertEqual(config.response_quality_threshold, 0.8)
        self.assertEqual(config.user_satisfaction_threshold, 0.9)
        self.assertEqual(config.feedback_processing_interval, 600)
        self.assertFalse(config.quality_analysis_enabled)
        self.assertFalse(config.real_time_improvements)


@unittest.skipIf(not VPA_IMPORTS_AVAILABLE, "VPA imports not available")
class TestCreateEnhancedVPASystem(unittest.TestCase):
    """Test enhanced VPA system creation."""
    
    async def test_create_enhanced_system_default_config(self):
        """Test creating enhanced system with default config."""
        enhancer = await create_enhanced_vpa_system()
        
        self.assertIsInstance(enhancer, VPAUXEnhancer)
        self.assertIsInstance(enhancer.config, UXEnhancementConfig)
        self.assertIsInstance(enhancer.quality_analyzer, VPAQualityAnalyzer)
        self.assertIsInstance(enhancer.feedback_processor, VPAFeedbackProcessor)
    
    async def test_create_enhanced_system_custom_config(self):
        """Test creating enhanced system with custom config."""
        custom_config = UXEnhancementConfig(
            enable_response_streaming=False,
            enable_suggestion_chips=True,
            response_quality_threshold=0.8,
            quality_analysis_enabled=True
        )
        
        enhancer = await create_enhanced_vpa_system(custom_config)
        
        self.assertIsInstance(enhancer, VPAUXEnhancer)
        self.assertEqual(enhancer.config, custom_config)
        self.assertFalse(enhancer.config.enable_response_streaming)
        self.assertTrue(enhancer.config.enable_suggestion_chips)
        self.assertEqual(enhancer.config.response_quality_threshold, 0.8)


class VPAQualityUXEnhancementsTestSuite:
    """
    Comprehensive test suite for VPA Quality & UX Enhancements.
    """
    
    def __init__(self):
        """Initialize the test suite."""
        self.test_results = {
            "suite_name": "VPA Quality & UX Enhancements Test Suite",
            "milestone": "Quality & UX Enhancements",
            "test_timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "test_categories": {
                "quality_metrics": {"passed": 0, "failed": 0, "skipped": 0},
                "user_feedback": {"passed": 0, "failed": 0, "skipped": 0},
                "quality_analyzer": {"passed": 0, "failed": 0, "skipped": 0},
                "feedback_processor": {"passed": 0, "failed": 0, "skipped": 0},
                "ux_enhancer": {"passed": 0, "failed": 0, "skipped": 0},
                "configuration": {"passed": 0, "failed": 0, "skipped": 0},
                "system_integration": {"passed": 0, "failed": 0, "skipped": 0}
            },
            "detailed_results": []
        }
    
    async def run_all_tests(self):
        """Run all tests in the suite."""
        print("🚀 Running VPA Quality & UX Enhancements Test Suite")
        print("=" * 60)
        
        # Run unittest test cases
        test_classes = [
            TestQualityMetrics,
            TestUserFeedback,
            TestVPAQualityAnalyzer,
            TestVPAFeedbackProcessor,
            TestVPAUXEnhancer,
            TestUXEnhancementConfig,
            TestCreateEnhancedVPASystem
        ]
        
        for test_class in test_classes:
            if VPA_IMPORTS_AVAILABLE or test_class in [TestQualityMetrics, TestUserFeedback]:
                await self._run_test_class(test_class)
            else:
                print(f"⏭️  Skipping {test_class.__name__} (VPA imports not available)")
        
        # Generate summary
        self._generate_summary()
        
        return self.test_results
    
    async def _run_test_class(self, test_class):
        """Run a specific test class."""
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Update results
        category = self._get_test_category(test_class.__name__)
        self.test_results["test_categories"][category]["passed"] += result.testsRun - len(result.failures) - len(result.errors)
        self.test_results["test_categories"][category]["failed"] += len(result.failures) + len(result.errors)
        self.test_results["test_categories"][category]["skipped"] += len(result.skipped)
        
        self.test_results["total_tests"] += result.testsRun
        self.test_results["passed_tests"] += result.testsRun - len(result.failures) - len(result.errors)
        self.test_results["failed_tests"] += len(result.failures) + len(result.errors)
        self.test_results["skipped_tests"] += len(result.skipped)
    
    def _get_test_category(self, test_class_name):
        """Get test category from class name."""
        if "QualityMetrics" in test_class_name:
            return "quality_metrics"
        elif "UserFeedback" in test_class_name:
            return "user_feedback"
        elif "QualityAnalyzer" in test_class_name:
            return "quality_analyzer"
        elif "FeedbackProcessor" in test_class_name:
            return "feedback_processor"
        elif "UXEnhancer" in test_class_name:
            return "ux_enhancer"
        elif "Config" in test_class_name:
            return "configuration"
        else:
            return "system_integration"
    
    def _generate_summary(self):
        """Generate test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        print(f"Skipped: {self.test_results['skipped_tests']}")
        
        if self.test_results['total_tests'] > 0:
            success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 CATEGORY BREAKDOWN:")
        for category, stats in self.test_results["test_categories"].items():
            total = stats["passed"] + stats["failed"] + stats["skipped"]
            if total > 0:
                print(f"{category}: {stats['passed']}/{total} passed")
        
        # Overall status
        if self.test_results['failed_tests'] == 0:
            print("\n✅ All tests passed!")
            self.test_results["overall_status"] = "PASSED"
        else:
            print(f"\n❌ {self.test_results['failed_tests']} tests failed!")
            self.test_results["overall_status"] = "FAILED"
    
    def save_results(self, filename="quality_ux_test_results.json"):
        """Save test results to file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"\n📁 Test results saved to {filename}")
        except Exception as e:
            print(f"❌ Failed to save test results: {e}")


async def main():
    """Main test execution function."""
    # Create and run test suite
    test_suite = VPAQualityUXEnhancementsTestSuite()
    results = await test_suite.run_all_tests()
    
    # Save results
    test_suite.save_results()
    
    # Exit with appropriate code
    if results["overall_status"] == "PASSED":
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
