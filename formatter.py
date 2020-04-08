import sublime, sublime_plugin, subprocess, difflib, os


def diff_sanity_check(a, b):
	if a != b:
		raise Exception("diff sanity check mismatch\n-%s\n+%s" % (a, b))

class CppformatCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		src = view.substr(sublime.Region(0, view.size()))
		gofmt = subprocess.Popen(["clang-format"],
			stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		sout, serr = gofmt.communicate(src.encode())
		if gofmt.returncode != 0:
			print(serr.decode(), end="")
			return

		newsrc = sout.decode()
		diff = difflib.ndiff(src.splitlines(), newsrc.splitlines())
		i = 0
		for line in diff:
			if line.startswith("?"): # skip hint lines
				continue

			l = (len(line)-2)+1
			if line.startswith("-"):
				diff_sanity_check(view.substr(sublime.Region(i, i+l-1)), line[2:])
				view.erase(edit, sublime.Region(i, i+l))
			elif line.startswith("+"):
				view.insert(edit, i, line[2:]+"\n")
				i += l
			else:
				diff_sanity_check(view.substr(sublime.Region(i, i+l-1)), line[2:])
				i += l


class Cppformat(sublime_plugin.EventListener):
	"""Sublime Text gocode integration."""
	
	def on_pre_save(self, view):
		# print(view.scope_name(0)) # get scope name
		if view.scope_name(0).split(' ')[0] not in ["source.c++", "source.c"]:
			return
		view.run_command('cppformat')
