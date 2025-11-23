using RenphoGarminSync.Console.Models;
using System;
using System.IO;
using System.Text.Json;

namespace RenphoGarminSync.Console
{
    public static class ConfigurationHelper
    {
        private static AppConfig _appConfig;
        public static AppConfig GetApplicationConfig()
        {
            if (_appConfig is not null)
                return _appConfig;

            var filePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "config.json");
            if (!File.Exists(filePath))
                throw new InvalidOperationException("Config file couldn't be found");

            var fileContent = File.ReadAllText(filePath);
            _appConfig = JsonSerializer.Deserialize<AppConfig>(fileContent);

            if (_appConfig is null)
                throw new InvalidOperationException("Failed to deserialize configuration file.");

            if (_appConfig.Garmin is null)
                throw new InvalidOperationException("Configuration is missing 'Garmin' section.");

            if (_appConfig.Renpho is null)
                throw new InvalidOperationException("Configuration is missing 'Renpho' section.");

            if (_appConfig.General is null)
                throw new InvalidOperationException("Configuration is missing 'General' section.");

            return _appConfig;
        }
    }
}
