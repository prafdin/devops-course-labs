# ЭТАП 1: Сборка
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env
WORKDIR /app

COPY Csharp-example.sln ./
COPY ExampleWebService/ExampleWebService.csproj ./ExampleWebService/
COPY ExampleTestProject/ExampleTestProject.csproj ./ExampleTestProject/
RUN dotnet restore

COPY . ./
RUN dotnet publish ExampleWebService/ExampleWebService.csproj -c Release -o out

# ЭТАП 2: Запуск
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY --from=build-env /app/out .

# Настройка порта внутри контейнера
ENV ASPNETCORE_URLS=http://+:8181
EXPOSE 8181

# Запекаем хэш коммита в образ на этапе сборки (CI)
ARG DEPLOY_REF=N/A
ENV DEPLOY_REF=$DEPLOY_REF

ENTRYPOINT ["dotnet", "ExampleWebService.dll"]
