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

-- UltiSnips configuration (compatible with Gilles Castel style workflow).
vim.g.UltiSnipsExpandTrigger = "<tab>"
vim.g.UltiSnipsJumpForwardTrigger = "<tab>"
vim.g.UltiSnipsJumpBackwardTrigger = "<s-tab>"
vim.g.UltiSnipsSnippetDirectories = { "UltiSnips" }

add_current_notebook_to_rtp()
