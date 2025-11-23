FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy solution and project files
COPY ["RenphoGarminSync.sln", "./"]
COPY ["RenphoGarminSync.Console/RenphoGarminSync.Console.csproj", "RenphoGarminSync.Console/"]
COPY ["RenphoGarminSync.Garmin.Api/RenphoGarminSync.Garmin.Api.csproj", "RenphoGarminSync.Garmin.Api/"]
COPY ["RenphoGarminSync.Garmin.Auth/RenphoGarminSync.Garmin.Auth.csproj", "RenphoGarminSync.Garmin.Auth/"]
COPY ["RenphoGarminSync.Garmin.Shared/RenphoGarminSync.Garmin.Shared.csproj", "RenphoGarminSync.Garmin.Shared/"]
COPY ["RenphoGarminSync.Renpho.Api/RenphoGarminSync.Renpho.Api.csproj", "RenphoGarminSync.Renpho.Api/"]
COPY ["RenphoGarminSync.Renpho.Auth/RenphoGarminSync.Renpho.Auth.csproj", "RenphoGarminSync.Renpho.Auth/"]
COPY ["RenphoGarminSync.Renpho.Shared/RenphoGarminSync.Renpho.Shared.csproj", "RenphoGarminSync.Renpho.Shared/"]

# Restore dependencies
RUN dotnet restore

# Copy the rest of the source code
COPY . .

# Build and publish
WORKDIR "/src/RenphoGarminSync.Console"
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/runtime:8.0 AS final
WORKDIR /app
COPY --from=build /app/publish .

# Create directory for persistence
RUN mkdir -p Persistence

ENTRYPOINT ["dotnet", "rgs.dll"]
