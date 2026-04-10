local function project_root()
  local dir = vim.fn.getcwd()
  while dir and dir ~= "" and dir ~= "/" do
    if vim.fn.filereadable(dir .. "/scripts/create_figure.sh") == 1 then
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

local function vimtex_root_or_cwd()
  if vim.b.vimtex and vim.b.vimtex.root then
    return vim.b.vimtex.root
  end
  return vim.fn.getcwd()
end

vim.keymap.set("n", "<leader>i", function()
  local title = vim.fn.input("Figure title: ")
  if title == "" then
    return
  end
  local name = title:gsub("%s+", "-"):lower()
  local root = vimtex_root_or_cwd()
  local figdir = root .. "/figures"
  local cmd = project_root() .. "/scripts/create_figure.sh "
    .. vim.fn.shellescape(name) .. " "
    .. vim.fn.shellescape(figdir)
  local job = vim.fn.jobstart(cmd, { detach = true })
  if job <= 0 then
    print("Failed to launch create_figure.sh")
    return
  end

  local lines = {
    "\\begin{figure}[ht]",
    "    \\centering",
    "    \\incfig{" .. name .. "}",
    "    \\caption{" .. title .. "}",
    "    \\label{fig:" .. name .. "}",
    "\\end{figure}",
    "",
  }
  vim.api.nvim_put(lines, "l", true, true)
  vim.cmd("write")
end, { desc = "Create figure (script watcher mode)" })

vim.keymap.set("n", "<leader>I", function()
  local root = vimtex_root_or_cwd()
  local figdir = root .. "/figures/"
  local cmd = project_root() .. "/bin/inkfig edit " .. vim.fn.shellescape(figdir) .. " > /dev/null 2>&1 &"
  vim.cmd("silent exec '!" .. cmd .. "'")
  vim.cmd("redraw!")
end, { desc = "Pick and edit Inkscape figure" })
