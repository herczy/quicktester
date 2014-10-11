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
let g:quicktester = 1
let g:nosefailed = 0

fun! s:get_python()
  if exists('t:python')
    let command = t:python
  elseif exists('g:python')
    let command = g:python
  else
    let command = 'python'
  endif

  return command
endfun

fun! s:check_quicktester()
  if !g:quicktester
    return 0
  endif

  exec system(s:get_python() . ' -c "import quicktester"')
  return !v:shell_error
endfun

fun! s:get_nosetest()
  return s:get_python() . ' $(which nosetests)'
endfun

fun! s:run_nosetests(...)
  let nose = s:get_nosetest()
  let command = ':!' . nose . ' -s'

  if a:0 > 0
    let command = command . ' ' . a:1
  endif

  execute command
  if v:shell_error
    let g:nosefailed = 1
  endif
endfun

fun! s:run_quicktest(...)
  if !s:check_quicktester()
    let args = ''
    if a:0 > 0
      let args = a:1
    endif

    call s:run_nosetests(args)
    return
  endif

  let command = '-Q /tmp/nose-quickfix'

  if g:nosefailed
    let command = command . ' --run-count 1'
  else
    let command = command . ' --git-changes'
  endif

  if a:0 > 0
    let command = command . ' ' . a:1
  endif

  call s:run_nosetests(command)
  if g:nosefailed
    cgetfile /tmp/nose-quickfix
    echom 'Use :cn or :cp to switch between errors'
  endif
endfun

command! -nargs=* -complete=file_in_path Quicktest :call s:run_quicktest('<args>')
command! -nargs=* -complete=file_in_path Nose :call s:run_nosetests('<args>')
