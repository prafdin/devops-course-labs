FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env
WORKDIR /app

# Копирование файлов решений и проектов для восстановления зависимостей
COPY Csharp-example.sln ./
COPY ExampleWebService/ExampleWebService.csproj ./ExampleWebService/
COPY ExampleTestProject/ExampleTestProject.csproj ./ExampleTestProject/
RUN dotnet restore

# Копирование исходного кода и сборка проекта
COPY . ./
RUN dotnet publish ExampleWebService/ExampleWebService.csproj -c Release -o out

# Этап запуска приложения
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build-env /app/out .

# Настройка порта внутри контейнера
ENV ASPNETCORE_URLS=http://+:8181
EXPOSE 8181

ENTRYPOINT ["dotnet", "ExampleWebService.dll"]
