"""
Test data for trivia-related tests.
Contains constants and test data fixtures.
"""

from typing import TypedDict, List

class AnswerData(TypedDict):
    answer_title: str
    is_correct: bool

class QuestionData(TypedDict):
    question_title: str
    answers: List[AnswerData]

class TriviaData(TypedDict):
    title: str
    difficulty: int
    theme: str
    username: str
    questions: List[QuestionData]

class ExpectedCounts(TypedDict):
    admin: int
    user: int
    anonymous: int

class TriviaPermissionData(TypedDict):
    title: str
    difficulty: int
    is_public: bool
    created_by_other: bool

class PermissionTestData(TypedDict):
    expected_counts: ExpectedCounts
    trivias: List[TriviaPermissionData]

TEST_QUESTIONS = {
    'valid_question': {
        'question_title': 'Test Question',
        'answers': [
            {'answer_title': 'Correct Answer', 'is_correct': True},
            {'answer_title': 'Wrong Answer', 'is_correct': False}
        ]
    },
    'invalid_question': {
        'question_title': 'Invalid Question',
        'answers': []  # Invalid: no answers
    }
}

TEST_TRIVIA_DATA = {
    'valid_trivia': {
        'title': 'Test Trivia',
        'difficulty': 1,
        'theme': 'Python',
        'username': 'testuser',
        'questions': [
            {
                'question_title': 'What is Python?',
                'answers': [
                    {'answer_title': 'A programming language', 'is_correct': True},
                    {'answer_title': 'A snake', 'is_correct': False}
                ]
            },
            {
                'question_title': 'Is Python interpreted?',
                'answers': [
                    {'answer_title': 'Yes', 'is_correct': True},
                    {'answer_title': 'No', 'is_correct': False}
                ]
            },
            {
                'question_title': 'Who created Python?',
                'answers': [
                    {'answer_title': 'Guido van Rossum', 'is_correct': True},
                    {'answer_title': 'Linus Torvalds', 'is_correct': False}
                ]
            }
        ]
    },
    'invalid_trivia': {
        'title': 'Invalid Trivia',
        'difficulty': 1,
        'theme': 'Python',
        'username': 'testuser',
        'questions': []  # Invalid: no questions
    },
    'update_data': {
        'basic': {
            'title': 'Updated Title',
            'username': 'testuser'
        },
        'full': {
            'title': 'Fully Updated Trivia',
            'difficulty': 2,
            'theme': 'Python',
            'username': 'testuser',
            'is_public': False,
            'questions': [
                {
                    'question_title': 'Updated Question 1',
                    'answers': [
                        {'answer_title': 'New Correct Answer', 'is_correct': True},
                        {'answer_title': 'New Wrong Answer', 'is_correct': False}
                    ]
                },
                {
                    'question_title': 'Updated Question 2',
                    'answers': [
                        {'answer_title': 'Another Correct Answer', 'is_correct': True},
                        {'answer_title': 'Another Wrong Answer', 'is_correct': False}
                    ]
                },
                {
                    'question_title': 'Updated Question 3',
                    'answers': [
                        {'answer_title': 'Third Correct Answer', 'is_correct': True},
                        {'answer_title': 'Third Wrong Answer', 'is_correct': False}
                    ]
                }
            ]
        },
        'questions': {
            'questions': [
                {
                    'question_title': 'Updated Question',
                    'answers': [
                        {'answer_title': 'Updated Correct Answer', 'is_correct': True},
                        {'answer_title': 'Updated Wrong Answer', 'is_correct': False}
                    ]
                }
            ]
        }
    },
    'complex_trivia': {
        'title': 'Complex Performance Test Trivia',
        'difficulty': 1,
        'theme': 'Python',
        'username': 'testuser',
        'questions': [
            {
                'question_title': f'Performance Question {i}',
                'answers': [
                    {'answer_title': f'Answer {j} for question {i}', 
                     'is_correct': j == 0}
                    for j in range(4)
                ]
            }
            for i in range(5)
        ]
    },
    'concurrent_trivia': {
        'title': 'Concurrent Trivia Template',  # Se modificará con el thread ID
        'difficulty': 1,
        'theme': 'Python',
        'username': 'testuser',
        'questions': [
            {
                'question_title': 'Concurrent Question 1',
                'answers': [
                    {'answer_title': 'Correct Answer 1', 'is_correct': True},
                    {'answer_title': 'Wrong Answer 1', 'is_correct': False}
                ]
            },
            {
                'question_title': 'Concurrent Question 2',
                'answers': [
                    {'answer_title': 'Correct Answer 2', 'is_correct': True},
                    {'answer_title': 'Wrong Answer 2', 'is_correct': False}
                ]
            },
            {
                'question_title': 'Concurrent Question 3',
                'answers': [
                    {'answer_title': 'Correct Answer 3', 'is_correct': True},
                    {'answer_title': 'Wrong Answer 3', 'is_correct': False}
                ]
            }
        ]
    }
}

ERROR_MESSAGES = {
    'NO_QUESTIONS': 'A trivia must have at least 3 questions',
    'NO_ANSWERS': 'must have at least 2 answers',
    'NO_CORRECT_ANSWER': 'must have at least one correct answer',
    'DUPLICATE_TITLE': 'trivia with this Title already exists.',
    'INVALID_DIFFICULTY': '"5" is not a valid choice.',
    'USER_NOT_FOUND': 'User not found',
    'UNAUTHORIZED': 'Authentication credentials were not provided.',
    'FORBIDDEN': 'You do not have permission to perform this action.',
    'CACHE_ERROR': 'Cache should contain trivia data',
    'PERFORMANCE_ERROR': 'Response time exceeded acceptable limit',
    'CONCURRENT_ERROR': 'Concurrent creation failed'
}

TEST_PERMISSION_DATA: PermissionTestData = {
    'expected_counts': {
        'admin': 2,     # Admin sees public trivias and their own trivias
        'user': 2,      # User sees public trivias and their own trivias
        'anonymous': 1  # Anonymous user sees only public trivias
    },
    'trivias': [
        {
            'title': 'Public Trivia',
            'difficulty': 1,
            'is_public': True,
            'created_by_other': True
        },
        {
            'title': 'Own Private Trivia',
            'difficulty': 1,
            'is_public': False,
            'created_by_other': False
        }
    ]
} 