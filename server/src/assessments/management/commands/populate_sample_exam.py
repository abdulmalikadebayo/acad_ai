"""
Management command to populate database with realistic university-level exam data.
Aligned with Acad AI's domain: academic assessments for Nigerian universities.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from assessments.constants import QuestionType
from assessments.models import Choice, Course, Exam, Question


class Command(BaseCommand):
    help = "Create realistic academic exam data for testing the assessment engine"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("=" * 70))
        self.stdout.write(
            self.style.WARNING("Creating Academic Sample Exams (Acad AI Demo Data)")
        )
        self.stdout.write(self.style.WARNING("=" * 70))

        self._create_computer_science_exam()
        self._create_political_science_exam()
        self._create_economics_exam()

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(
            self.stdout.write(
                self.style.SUCCESS("All sample exams created successfully!")
            )
        )
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write("\nYou can now test with:")
        self.stdout.write("  • GET /assessments/exams/")
        self.stdout.write("  • POST /assessments/exams/{id}/submissions/")
        self.stdout.write("")

    def _create_computer_science_exam(self):
        """Create Computer Science exam (aligned with Babcock University example)"""
        self.stdout.write("\nCreating Computer Science Exam...")

        course, _ = Course.objects.get_or_create(
            code="CSC201", defaults={"name": "Data Structures and Algorithms"}
        )

        exam, created = Exam.objects.get_or_create(
            title="CSC201 Midterm Examination",
            course=course,
            defaults={
                "duration_minutes": 90,
                "is_active": True,
                "starts_at": timezone.now() - timedelta(days=1),
                "ends_at": timezone.now() + timedelta(days=30),
                "metadata": {"semester": "First Semester 2025/2026", "level": "200"},
            },
        )
        if not created:
            self.stdout.write(
                self.style.WARNING(f"  Exam already exists: {exam.title}")
            )
            return

        # MCQ Questions
        q1 = Question.objects.create(
            exam=exam,
            type=QuestionType.MCQ,
            prompt="What is the time complexity of binary search in a sorted array?",
            expected_answer="O(log n)",
            points=3,
            order=1,
            metadata={
                "difficulty": "medium",
                "topic": "Algorithms",
                "subtopic": "Searching Algorithms",
                "bloom_level": "remember",
                "time_estimate_seconds": 45,
                "tags": ["algorithms", "complexity", "binary-search"],
            },
        )
        Choice.objects.create(question=q1, text="O(n)", is_correct=False)
        Choice.objects.create(question=q1, text="O(log n)", is_correct=True)
        Choice.objects.create(question=q1, text="O(n²)", is_correct=False)
        Choice.objects.create(question=q1, text="O(1)", is_correct=False)

        q2 = Question.objects.create(
            exam=exam,
            type=QuestionType.MCQ,
            prompt="Which data structure uses LIFO (Last In First Out) principle?",
            expected_answer="Stack",
            points=3,
            order=2,
            metadata={
                "difficulty": "easy",
                "topic": "Data Structures",
                "subtopic": "Stack",
                "bloom_level": "remember",
                "time_estimate_seconds": 30,
                "tags": ["data-structures", "stack", "LIFO"],
            },
        )
        Choice.objects.create(question=q2, text="Queue", is_correct=False)
        Choice.objects.create(question=q2, text="Stack", is_correct=True)
        Choice.objects.create(question=q2, text="Tree", is_correct=False)
        Choice.objects.create(question=q2, text="Graph", is_correct=False)

        q3 = Question.objects.create(
            exam=exam,
            type=QuestionType.MCQ,
            prompt="In object-oriented programming, which principle allows a class to inherit properties from another class?",
            expected_answer="Inheritance",
            points=3,
            order=3,
            metadata={
                "difficulty": "easy",
                "topic": "Object-Oriented Programming",
                "subtopic": "OOP Principles",
                "bloom_level": "understand",
                "time_estimate_seconds": 40,
                "tags": ["OOP", "inheritance", "fundamentals"],
            },
        )
        Choice.objects.create(question=q3, text="Encapsulation", is_correct=False)
        Choice.objects.create(question=q3, text="Polymorphism", is_correct=False)
        Choice.objects.create(question=q3, text="Inheritance", is_correct=True)
        Choice.objects.create(question=q3, text="Abstraction", is_correct=False)

        # Theory Questions
        q4 = Question.objects.create(
            exam=exam,
            type=QuestionType.SHORT_TEXT,
            prompt="Define what a linked list is and explain its advantages over an array. Provide at least two key differences.",
            expected_answer="A linked list is a linear data structure where elements (nodes) are connected through pointers, with each node containing data and a reference to the next node. Advantages over arrays include: (1) Dynamic size - linked lists can grow or shrink during runtime without reallocation, (2) Efficient insertion/deletion - adding or removing elements doesn't require shifting other elements like in arrays. However, linked lists have slower random access (O(n)) compared to arrays (O(1)) and require extra memory for storing pointers.",
            points=12,
            order=4,
            metadata={
                "difficulty": "medium",
                "topic": "Data Structures",
                "subtopic": "Linked Lists",
                "bloom_level": "understand",
                "time_estimate_seconds": 420,
                "tags": ["data-structures", "linked-list", "arrays", "comparison"],
                "requires_example": True,
            },
        )

        q5 = Question.objects.create(
            exam=exam,
            type=QuestionType.SHORT_TEXT,
            prompt="Explain the concept of recursion in programming. Provide a real-world example where recursion would be appropriate, and discuss one advantage and one disadvantage of using recursive solutions.",
            expected_answer="Recursion is a programming technique where a function calls itself to solve smaller instances of the same problem until it reaches a base case. Example: Calculating factorial (5! = 5 × 4 × 3 × 2 × 1) where factorial(n) = n × factorial(n-1) with base case factorial(1) = 1. Another example is traversing tree structures like file systems. Advantage: Recursion provides elegant, readable solutions for naturally recursive problems like tree traversal. Disadvantage: Recursive solutions can consume significant memory through function call stack and may be slower than iterative solutions due to function call overhead.",
            points=15,
            order=5,
            metadata={
                "difficulty": "hard",
                "topic": "Programming Techniques",
                "subtopic": "Recursion",
                "bloom_level": "apply",
                "time_estimate_seconds": 540,
                "tags": ["recursion", "algorithms", "function-calls"],
                "requires_example": True,
                "cognitive_demand": "high",
            },
        )

        q6 = Question.objects.create(
            exam=exam,
            type=QuestionType.SHORT_TEXT,
            prompt="Describe the difference between a stack and a queue. For each data structure, provide one real-world application where it would be most appropriate to use.",
            expected_answer="Stack is a LIFO (Last In First Out) data structure where elements are added and removed from the same end (top). Queue is a FIFO (First In First Out) structure where elements are added at one end (rear) and removed from the other (front). Real-world applications: Stack is ideal for browser history (back button), undo mechanisms in text editors, and function call management. Queue is perfect for print job scheduling, customer service systems, and task scheduling in operating systems where first-come-first-served order matters.",
            points=12,
            order=6,
            metadata={
                "difficulty": "medium",
                "topic": "Data Structures",
                "subtopic": "Stack and Queue",
                "bloom_level": "analyze",
                "time_estimate_seconds": 360,
                "tags": ["data-structures", "stack", "queue", "comparison"],
                "requires_example": True,
            },
        )

        self.stdout.write(self.style.SUCCESS(f"  Created {exam.title}"))
        self.stdout.write(f"     - 3 MCQ questions (9 points)")
        self.stdout.write(f"     - 3 Theory questions (39 points)")
        self.stdout.write(f"     - Total: 48 points")

    def _create_political_science_exam(self):
        """Create Political Science exam (aligned with Dr. Chinedu Eti example)"""
        self.stdout.write("\nCreating Political Science Exam...")

        course, _ = Course.objects.get_or_create(
            code="POL301", defaults={"name": "Comparative Politics"}
        )

        exam, created = Exam.objects.get_or_create(
            title="POL301 End of Semester Examination",
            course=course,
            defaults={
                "duration_minutes": 120,
                "is_active": True,
                "starts_at": timezone.now() - timedelta(days=2),
                "ends_at": timezone.now() + timedelta(days=25),
                "metadata": {"semester": "Second Semester 2025/2026", "level": "300"},
            },
        )
        if not created:
            self.stdout.write(
                self.style.WARNING(f"  Exam already exists: {exam.title}")
            )
            return

        q1 = Question.objects.create(
            exam=exam,
            type=QuestionType.MCQ,
            prompt="Which form of government is characterized by the separation of powers among the executive, legislative, and judicial branches?",
            expected_answer="Presidential system",
            points=4,
            order=1,
            metadata={
                "difficulty": "easy",
                "topic": "Comparative Politics",
                "subtopic": "Forms of Government",
                "bloom_level": "remember",
                "time_estimate_seconds": 45,
                "tags": [
                    "government-systems",
                    "separation-of-powers",
                    "presidentialism",
                ],
            },
        )
        Choice.objects.create(
            question=q1, text="Parliamentary system", is_correct=False
        )
        Choice.objects.create(question=q1, text="Presidential system", is_correct=True)
        Choice.objects.create(question=q1, text="Monarchy", is_correct=False)
        Choice.objects.create(question=q1, text="Totalitarian system", is_correct=False)

        q2 = Question.objects.create(
            exam=exam,
            type=QuestionType.MCQ,
            prompt="The concept of 'checks and balances' is primarily associated with which political philosopher?",
            expected_answer="Montesquieu",
            points=4,
            order=2,
            metadata={
                "difficulty": "medium",
                "topic": "Political Philosophy",
                "subtopic": "Enlightenment Thinkers",
                "bloom_level": "remember",
                "time_estimate_seconds": 60,
                "tags": [
                    "political-philosophy",
                    "checks-and-balances",
                    "Montesquieu",
                    "enlightenment",
                ],
            },
        )
        Choice.objects.create(question=q2, text="John Locke", is_correct=False)
        Choice.objects.create(question=q2, text="Montesquieu", is_correct=True)
        Choice.objects.create(question=q2, text="Thomas Hobbes", is_correct=False)
        Choice.objects.create(
            question=q2, text="Jean-Jacques Rousseau", is_correct=False
        )

        q3 = Question.objects.create(
            exam=exam,
            type=QuestionType.SHORT_TEXT,
            prompt="Discuss the main differences between federal and unitary systems of government. Using Nigeria and the United Kingdom as examples, explain how power is distributed in each system.",
            expected_answer="Federal systems divide power between central and regional governments (states/provinces) with each level having constitutionally protected autonomy. Unitary systems concentrate power in a central government that may delegate authority to local units. Nigeria operates a federal system where power is shared between federal government and 36 states, with each tier having specific responsibilities outlined in the constitution. The UK operates a unitary system where Parliament in London holds supreme authority and devolves powers to Scotland, Wales, and Northern Ireland at its discretion. Key difference: in federalism, regional governments have guaranteed constitutional powers that cannot be easily revoked, while in unitary systems, central government can modify or withdraw delegated powers.",
            points=18,
            order=3,
            metadata={
                "difficulty": "hard",
                "topic": "Comparative Politics",
                "subtopic": "Federal vs Unitary Systems",
                "bloom_level": "analyze",
                "time_estimate_seconds": 600,
                "tags": [
                    "federalism",
                    "unitary-system",
                    "Nigeria",
                    "UK",
                    "power-distribution",
                    "comparative-analysis",
                ],
                "requires_example": True,
                "cognitive_demand": "high",
            },
        )

        q4 = Question.objects.create(
            exam=exam,
            type=QuestionType.SHORT_TEXT,
            prompt="Analyze the role of political parties in democratic governance. What are the key functions they perform, and what challenges do multi-party systems face in developing democracies like Nigeria?",
            expected_answer="Political parties serve crucial functions in democracy: (1) Aggregating diverse interests and forming coherent policy platforms, (2) Recruiting and training political leaders, (3) Mobilizing voters and facilitating political participation, (4) Providing organized opposition and accountability mechanisms. In Nigeria's multi-party system, challenges include: ethnic and regional fragmentation leading to parties based on identity rather than ideology, lack of internal democracy with leadership dominated by 'godfathers', defection culture where politicians switch parties for personal gain rather than principle, and weak institutionalization making parties dependent on individual personalities. These challenges undermine democratic consolidation and policy consistency.",
            points=20,
            order=4,
            metadata={
                "difficulty": "hard",
                "topic": "Democratic Governance",
                "subtopic": "Political Parties",
                "bloom_level": "analyze",
                "time_estimate_seconds": 660,
                "tags": [
                    "political-parties",
                    "democracy",
                    "Nigeria",
                    "multi-party-system",
                    "challenges",
                ],
                "requires_example": True,
                "cognitive_demand": "high",
            },
        )

        q5 = Question.objects.create(
            exam=exam,
            type=QuestionType.SHORT_TEXT,
            prompt="Explain the concept of democracy and discuss why free and fair elections are considered fundamental to democratic systems. What mechanisms help ensure election integrity?",
            expected_answer="Democracy is a system of government where power ultimately resides with the people, exercised through elected representatives. Core principles include political equality, majority rule with minority rights, and accountability. Free and fair elections are fundamental because they provide: (1) Legitimacy to government through popular consent, (2) Peaceful mechanism for leadership change, (3) Accountability as leaders must face voters periodically. Mechanisms ensuring integrity include: independent electoral bodies (like INEC in Nigeria), transparent voter registration, secret ballot to prevent coercion, presence of party agents and observers during voting and counting, legal frameworks criminalizing electoral fraud, and judicial review of disputed results. Without credible elections, democracy becomes hollow as citizens cannot truly choose their leaders.",
            points=18,
            order=5,
            metadata={
                "difficulty": "medium",
                "topic": "Democratic Governance",
                "subtopic": "Elections and Electoral Integrity",
                "bloom_level": "understand",
                "time_estimate_seconds": 540,
                "tags": [
                    "democracy",
                    "elections",
                    "electoral-integrity",
                    "INEC",
                    "accountability",
                ],
                "requires_example": True,
            },
        )

        self.stdout.write(self.style.SUCCESS(f"  Created {exam.title}"))
        self.stdout.write(f"     - 2 MCQ questions (8 points)")
        self.stdout.write(f"     - 3 Theory questions (56 points)")
        self.stdout.write(f"     - Total: 64 points")

    def _create_economics_exam(self):
        """Create Economics/Finance exam (aligned with Dr. Ayodeji Ajibade example)"""
        self.stdout.write("\nCreating Finance Exam...")

        course, _ = Course.objects.get_or_create(
            code="FIN202", defaults={"name": "Financial Management"}
        )

        exam, created = Exam.objects.get_or_create(
            title="FIN202 Continuous Assessment Test",
            course=course,
            defaults={
                "duration_minutes": 60,
                "is_active": True,
                "starts_at": timezone.now(),
                "ends_at": timezone.now() + timedelta(days=14),
                "metadata": {
                    "semester": "First Semester 2025/2026",
                    "level": "200",
                    "test_type": "CAT",
                },
            },
        )
        if not created:
            self.stdout.write(
                self.style.WARNING(f"  Exam already exists: {exam.title}")
            )
            return

        q1 = Question.objects.create(
            exam=exam,
            type=QuestionType.MCQ,
            prompt="What is the primary goal of financial management in a corporation?",
            expected_answer="Maximize shareholder wealth",
            points=3,
            order=1,
            metadata={
                "difficulty": "easy",
                "topic": "Financial Management Fundamentals",
                "subtopic": "Corporate Financial Goals",
                "bloom_level": "remember",
                "time_estimate_seconds": 30,
                "tags": [
                    "financial-management",
                    "shareholder-wealth",
                    "corporate-finance",
                ],
            },
        )
        Choice.objects.create(question=q1, text="Maximize revenue", is_correct=False)
        Choice.objects.create(question=q1, text="Minimize costs", is_correct=False)
        Choice.objects.create(
            question=q1, text="Maximize shareholder wealth", is_correct=True
        )
        Choice.objects.create(
            question=q1, text="Maximize market share", is_correct=False
        )

        q2 = Question.objects.create(
            exam=exam,
            type=QuestionType.MCQ,
            prompt="The time value of money concept states that:",
            expected_answer="Money available today is worth more than the same amount in the future",
            points=3,
            order=2,
            metadata={
                "difficulty": "easy",
                "topic": "Financial Management Fundamentals",
                "subtopic": "Time Value of Money",
                "bloom_level": "understand",
                "time_estimate_seconds": 40,
                "tags": ["time-value-of-money", "present-value", "future-value"],
            },
        )
        Choice.objects.create(
            question=q2,
            text="Money loses value over time due to inflation",
            is_correct=False,
        )
        Choice.objects.create(
            question=q2,
            text="Money available today is worth more than the same amount in the future",
            is_correct=True,
        )
        Choice.objects.create(
            question=q2,
            text="Future money is more valuable than present money",
            is_correct=False,
        )
        Choice.objects.create(
            question=q2,
            text="Time has no effect on the value of money",
            is_correct=False,
        )

        q3 = Question.objects.create(
            exam=exam,
            type=QuestionType.SHORT_TEXT,
            prompt="Define working capital and explain its importance in business operations. What happens when a company has insufficient working capital?",
            expected_answer="Working capital is the difference between a company's current assets (cash, inventory, receivables) and current liabilities (payables, short-term debt). It represents the funds available for day-to-day operations. Importance: (1) Ensures smooth operations by covering regular expenses like wages, utilities, and supplier payments, (2) Provides cushion for unexpected expenses or opportunities, (3) Indicates financial health and operational efficiency. Insufficient working capital leads to: inability to pay suppliers on time (damaged relationships), difficulty meeting payroll, missed business opportunities, potential insolvency even if profitable long-term, and loss of creditor confidence potentially triggering bankruptcy.",
            points=15,
            order=3,
            metadata={
                "difficulty": "medium",
                "topic": "Working Capital Management",
                "subtopic": "Current Assets and Liabilities",
                "bloom_level": "understand",
                "time_estimate_seconds": 480,
                "tags": [
                    "working-capital",
                    "liquidity",
                    "business-operations",
                    "financial-health",
                ],
                "requires_example": True,
            },
        )

        q4 = Question.objects.create(
            exam=exam,
            type=QuestionType.SHORT_TEXT,
            prompt="Explain the concept of diversification in investment portfolios. Why is it considered a risk management strategy? Provide a practical example.",
            expected_answer="Diversification is the practice of spreading investments across various asset classes, industries, or geographic regions to reduce risk. It works on the principle that different investments rarely move in perfect correlation - when some decline, others may rise or remain stable. This is risk management because it reduces unsystematic (company-specific) risk while maintaining exposure to market returns. Practical example: An investor with ₦1,000,000 might allocate 40% to Nigerian stocks (banking, telecoms, consumer goods), 30% to government bonds, 20% to real estate, and 10% to foreign stocks. If banking stocks fall due to regulatory changes, the impact on overall portfolio is cushioned by other holdings. Key principle: 'Don't put all eggs in one basket' - total portfolio loss requires multiple unrelated failures, which is statistically less likely.",
            points=14,
            order=4,
            metadata={
                "difficulty": "medium",
                "topic": "Investment Management",
                "subtopic": "Portfolio Diversification",
                "bloom_level": "apply",
                "time_estimate_seconds": 450,
                "tags": [
                    "diversification",
                    "risk-management",
                    "portfolio-theory",
                    "asset-allocation",
                ],
                "requires_example": True,
            },
        )

        self.stdout.write(self.style.SUCCESS(f"  Created {exam.title}"))
        self.stdout.write(f"     - 2 MCQ questions (6 points)")
        self.stdout.write(f"     - 2 Theory questions (29 points)")
        self.stdout.write(f"     - Total: 35 points")
