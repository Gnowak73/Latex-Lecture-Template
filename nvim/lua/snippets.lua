local function project_root()
  local dir = vim.fn.getcwd()
  while dir and dir ~= "" and dir ~= "/" do
    if vim.fn.filereadable(dir .. "/scripts/notes_manager.py") == 1 then
      return dir
    end
    local parent = vim.fn.fnamemodify(dir, ":h")
    if parent == dir then
      break
    end
    dir = parent
  end
  return vim.fn.getcwd()
end

local function add_current_notebook_to_rtp()
  local root = project_root()
  local current_link = root .. "/.current_course"
  if vim.fn.filereadable(current_link) == 0 and vim.fn.isdirectory(current_link) == 0 then
    return
  end
  local notebook = vim.fn.resolve(current_link)
  if vim.fn.isdirectory(notebook) == 1 then
    vim.opt.rtp:append(notebook)
  end
end

-- UltiSnips configuration.
-- Keep built-in triggers disabled so our <Tab>/<S-Tab> maps can choose
-- snippet actions only when available; otherwise they behave like normal keys.
vim.g.UltiSnipsExpandTrigger = "<Nop>"
vim.g.UltiSnipsJumpForwardTrigger = "<Nop>"
vim.g.UltiSnipsJumpBackwardTrigger = "<Nop>"
vim.g.UltiSnipsSnippetDirectories = { "UltiSnips" }

local function has_ultisnips()
  return vim.fn.exists("*UltiSnips#CanExpandSnippet") == 1
end

vim.keymap.set("i", "<Tab>", function()
  if has_ultisnips() then
    local can_expand = vim.fn["UltiSnips#CanExpandSnippet"]() == 1
    local can_jump = vim.fn["UltiSnips#CanJumpForwards"]() == 1
    if can_expand or can_jump then
      return vim.api.nvim_replace_termcodes("<C-R>=UltiSnips#ExpandSnippetOrJump()<CR>", true, true, true)
    end
  end
  return vim.api.nvim_replace_termcodes("<Tab>", true, true, true)
end, { expr = true, silent = true, desc = "UltiSnips expand/jump or tab" })

vim.keymap.set("i", "<S-Tab>", function()
  if has_ultisnips() and vim.fn["UltiSnips#CanJumpBackwards"]() == 1 then
    return vim.api.nvim_replace_termcodes("<C-R>=UltiSnips#JumpBackwards()<CR>", true, true, true)
  end
  return vim.api.nvim_replace_termcodes("<S-Tab>", true, true, true)
end, { expr = true, silent = true, desc = "UltiSnips jump backward or shift-tab" })

vim.keymap.set("i", "<CR>", function()
  if vim.bo.filetype == "tex" and vim.fn.pumvisible() == 1 then
    return vim.api.nvim_replace_termcodes("<C-e><CR>", true, true, true)
  end
  return vim.api.nvim_replace_termcodes("<CR>", true, true, true)
end, { expr = true, silent = true, desc = "Newline in TeX even when completion menu is open" })

add_current_notebook_to_rtp()
