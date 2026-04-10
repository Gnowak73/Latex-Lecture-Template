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

vim.keymap.set("n", "<leader>cn", function()
  local name = vim.fn.input("Course folder: ")
  if name == "" then return end
  local title = vim.fn.input("Course title: ")
  if title == "" then return end
  local short = vim.fn.input("Course short code: ")
  if short == "" then return end

  local cmd = project_root() .. "/bin/notes init-course "
    .. vim.fn.shellescape(name)
    .. " --title " .. vim.fn.shellescape(title)
    .. " --short " .. vim.fn.shellescape(short)

  vim.fn.system(cmd)
  print("Initialized course: " .. name)
end, { desc = "Initialize course" })

vim.keymap.set("n", "<leader>cs", function()
  local name = vim.fn.input("Set current course: ")
  if name == "" then return end
  vim.fn.system(project_root() .. "/bin/notes set-current " .. vim.fn.shellescape(name))
  print("Current course: " .. name)
end, { desc = "Set current course" })

vim.keymap.set("n", "<leader>ln", function()
  local title = vim.fn.input("Lecture title: ")
  vim.fn.system(project_root() .. "/bin/notes new-lecture --title " .. vim.fn.shellescape(title))
  print("Lecture created")
end, { desc = "New lecture" })

vim.keymap.set("n", "<leader>lo", function()
  vim.fn.system(project_root() .. "/bin/notes open-lecture last")
end, { desc = "Open latest lecture" })
