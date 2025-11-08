# Contributing to Study Buddy

Thank you for your interest in contributing to Study Buddy! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/study_buddy.git
   cd study_buddy
   ```
3. **Set up the development environment**
   ```bash
   docker-compose up -d
   ```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**
   - Run the backend: `cd backend && python -m app.main`
   - Run the frontend: `cd frontend && npm run dev`
   - Test all affected features

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Include screenshots if applicable

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints where appropriate
- Keep functions small and focused
- Add docstrings to functions and classes

Example:
```python
def process_document(file_path: str, file_type: str) -> List[Tuple[str, int, int]]:
    """
    Process document: extract text and chunk it

    Args:
        file_path: Path to the document file
        file_type: Type of file (pdf, docx, txt)

    Returns:
        List of tuples (chunk_text, page_number, chunk_index)
    """
    # Implementation
```

### JavaScript (Frontend)
- Use functional components
- Follow React best practices
- Use meaningful variable names
- Keep components small and reusable

Example:
```javascript
function DocumentItem({ document, onDelete }) {
  const handleDelete = () => {
    if (confirm('Are you sure?')) {
      onDelete(document.id);
    }
  };

  return (
    <div className="document-item">
      {/* Component content */}
    </div>
  );
}
```

## Areas for Contribution

### High Priority
- [ ] Streaming responses implementation
- [ ] Async document processing (Celery/RQ)
- [ ] More comprehensive error handling
- [ ] Unit tests for backend
- [ ] Integration tests for API
- [ ] Component tests for frontend

### Medium Priority
- [ ] Support for Excel files
- [ ] Support for PowerPoint files
- [ ] Image extraction from PDFs
- [ ] Document versioning
- [ ] Usage analytics
- [ ] Admin dashboard

### Low Priority
- [ ] Mobile app
- [ ] Browser extension
- [ ] Desktop app
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Collaborative features

## Adding New Features

### Backend Feature
1. Add models if needed in `backend/app/models/`
2. Add schemas in `backend/app/schemas/`
3. Add business logic in `backend/app/services/`
4. Add API endpoints in `backend/app/routers/`
5. Update documentation

### Frontend Feature
1. Create component in `frontend/src/components/`
2. Add page if needed in `frontend/src/pages/`
3. Add API calls in `frontend/src/services/api.js`
4. Update routes in `frontend/src/App.jsx`
5. Add styles in `frontend/src/styles/App.css`

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing Checklist
- [ ] User registration works
- [ ] Login works
- [ ] Document upload works
- [ ] Query works with all LLM providers
- [ ] Settings save correctly
- [ ] Error messages display properly
- [ ] All pages load correctly

## Documentation

### Code Documentation
- Add docstrings to Python functions
- Add JSDoc comments to complex JavaScript functions
- Comment complex algorithms

### User Documentation
- Update README.md for major features
- Update SETUP_GUIDE.md for setup changes
- Update QUICK_REFERENCE.md for new commands

## Commit Message Guidelines

Use clear, descriptive commit messages:

- `Add: new feature description`
- `Fix: bug description`
- `Update: what was updated`
- `Refactor: what was refactored`
- `Docs: documentation changes`
- `Style: formatting changes`
- `Test: test additions or changes`

Examples:
```
Add: streaming response support for queries
Fix: document upload progress bar not updating
Update: upgrade FastAPI to 0.110.0
Refactor: simplify RAG query logic
Docs: add troubleshooting section
```

## Pull Request Guidelines

### PR Title
Use the same format as commit messages:
- `Add: feature name`
- `Fix: bug description`

### PR Description
Include:
1. **What**: What changes were made
2. **Why**: Why these changes are needed
3. **How**: How the changes were implemented
4. **Testing**: How to test the changes
5. **Screenshots**: If UI changes

Template:
```markdown
## What
Brief description of changes

## Why
Reason for the changes

## How
Technical explanation

## Testing
1. Step to test
2. Step to test

## Screenshots
(if applicable)
```

## Bug Reports

When reporting bugs, include:
1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Exact steps to reproduce
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, browser, Docker version, etc.
6. **Logs**: Relevant error logs

## Feature Requests

When requesting features:
1. **Use Case**: Why is this feature needed
2. **Description**: What the feature should do
3. **Mockups**: UI mockups if applicable
4. **Alternatives**: Alternative solutions considered

## Code Review Process

All PRs will be reviewed for:
- Code quality and style
- Functionality
- Performance
- Security
- Documentation
- Tests

## Questions?

If you have questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with the "question" label

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers
- Focus on the code, not the person
- Assume good intentions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Study Buddy!
