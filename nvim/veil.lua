-- veil.nvim — hide sensitive values in .env files and other configs.
-- LazyVim / lazy.nvim spec.
--
-- Copy this into your plugin spec and make sure the block below is in the
-- same file as the rest of your LazyVim plugin declarations.
--
-- Commands:
--   :Veil         toggle veil on/off
--   :VeilEnable   enable veil
--   :VeilDisable  disable veil
--   :VeilPeek     reveal the value on the current line (auto-hides on leave)
--
-- Keymaps (overridable in the setup call):
--   <leader>sv    toggle veil
--   <leader>sp    peek at the value on the current line

{
  "Gentleman-Programming/veil.nvim",
  event = "VeryLazy",
  config = function()
    require("veil").setup({
      -- Files where veil is automatically enabled.
      files = {
        ".env",
        ".env.*",
        ".npmrc",
        ".pypirc",
        "credentials.json",
        "secrets.yaml",
        "secrets.yml",
        ".secrets",
      },

      -- Patterns to match. Group 2 is the value, and group 2 is concealed.
      patterns = {
        { pattern = "(%w+_KEY%s*[=:]%s*[\"']?)([^\"'\n]+)", group = 2 },
        { pattern = "(%w+_SECRET%s*[=:]%s*[\"']?)([^\"'\n]+)", group = 2 },
        { pattern = "(%w+_TOKEN%s*[=:]%s*[\"']?)([^\"'\n]+)", group = 2 },
        { pattern = "(%w+_PASSWORD%s*[=:]%s*[\"']?)([^\"'\n]+)", group = 2 },
        { pattern = "(%w+_CREDENTIAL%s*[=:]%s*[\"']?)([^\"'\n]+)", group = 2 },
      },

      conceal_char = "*",
      auto_enable = true,

      -- nil uses the colorscheme's Comment color.
      highlight = nil,

      -- Reveal values in insert mode on the current line.
      reveal_on_insert = false,

      keymaps = {
        toggle = "<leader>sv",
        peek = "<leader>sp",
      },
    })
  end,
}
