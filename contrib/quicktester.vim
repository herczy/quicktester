" quicktester.vim - Python quicktester plugin
" by Viktor Hercinger <hercinger.viktor@gmail.com>
" 
" Run only your relevant Python tests when TDD'ing.
"
" == Install ==
"
" Put this file into your ~/.vim/plugin directory.
"
" == Variables ==
"
" Specifying the Python version can be done with
" the t:python and g:python variables (precedence
" in that order). Otherwise the default Python
" version is used.

if exists('quicktester_loaded')
  finish
endif
let quicktester_loaded = 1

let s:QuickTester = {}

let s:QuickTester.enabled = 1
let s:QuickTester.last_call_failed = 1

fun! s:QuickTester.get_python()
  if exists('g:python')
    return g:python
  else
    return 'python'
  endif
endfun

fun! s:QuickTester.check_quicktester()
  if !self.enabled
    return 0
  endif

  exec system(self.get_python() . ' -c "import quicktester"')
  return !v:shell_error
endfun

fun! s:QuickTester.get_nosetest()
  let cmd = self.get_python() . ' -m nose'

  if exists('g:nose_extraargs')
    let cmd = cmd . ' ' . g:nose_extraargs
  endif

  return cmd
endfun

fun! s:QuickTester.run_nosetests(...)
  let nose = self.get_nosetest()
  let command = ':!' . nose . ' -s'

  if a:0 > 0
    let command = command . ' ' . a:1
  endif

  execute command
  if v:shell_error
    let self.last_call_failed = 1
  else
    let self.last_call_failed = 0
  endif
endfun

fun! s:QuickTester.run_quicktest(...)
  if !self.check_quicktester()
    let args = ''
    if a:0 > 0
      let args = a:1
    endif

    call self.run_nosetests(args)
    return
  endif

  let command = '-Q /tmp/nose-quickfix'

  if self.last_call_failed
    let command = command . ' --run-count 1'
  else
    let command = command . ' --git-changes'
  endif

  if a:0 > 0
    let command = command . ' ' . a:1
  endif

  call self.run_nosetests(command)
  if self.last_call_failed
    cgetfile /tmp/nose-quickfix
    echom 'Use :cn or :cp to switch between errors'
  endif
endfun

command! -nargs=* -complete=file_in_path Quicktest :call s:QuickTester.run_quicktest('<args>')
command! -nargs=* -complete=file_in_path Nose :call s:QuickTester.run_nosetests('<args>')
command! -nargs=+ SetPython :let g:python = '<args>'
