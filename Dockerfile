# ЭТАП 1: Сборка и компиляция проекта (используем тяжелый .NET SDK)
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env
WORKDIR /app

# Копируем файлы решений и проектов для восстановления зависимостей
COPY Csharp-example.sln ./
COPY ExampleWebService/ExampleWebService.csproj ./ExampleWebService/
COPY ExampleTestProject/ExampleTestProject.csproj ./ExampleTestProject/
RUN dotnet restore

# Копируем все остальные исходные файлы и компилируем приложение
COPY . ./
RUN dotnet publish ExampleWebService/ExampleWebService.csproj -c Release -o out

# ЭТАП 2: Запуск (используем легкую среду выполнения .NET Runtime)
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build-env /app/out .

# Настраиваем порт внутри контейнера
ENV ASPNETCORE_URLS=http://+:8181
EXPOSE 8181

# Команда запуска нашего приложения внутри контейнера
ENTRYPOINT ["dotnet", "ExampleWebService.dll"]
