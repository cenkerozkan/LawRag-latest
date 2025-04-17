docrepo:
	@read -p "Enter document repository name (e.g., custom_laws): " name; \
	classname=$$(echo $$name | awk -F_ '{for (i=1; i<=NF; ++i) {printf toupper(substr($$i,1,1)) substr($$i,2)} }')DocumentRepository; \
	filename="repository/$$name"_document_repository.py; \
	cp templates/template_document_repository.py.tpl $$filename; \
	sed -i '' "s/{{ClassName}}/$$classname/g" $$filename; \
	sed -i '' "s/{{name}}/$$name/g" $$filename; \
	echo "✅ Created $$filename with class $$classname"

git_count_lines:
	echo "Counting lines of code in the git repository"
	@git ls-files '*.py' | xargs wc -l