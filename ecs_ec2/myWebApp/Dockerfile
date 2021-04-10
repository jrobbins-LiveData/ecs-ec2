# https://dotnet.microsoft.com/learn/aspnet/hello-world-tutorial
# https://docs.docker.com/engine/examples/dotnetcore/
# https://stackoverflow.com/questions/64844197/docker-image-for-net-5
#
# docker build -t mywebapp .
# 
# docker run -p 8080:80 mywebapp

FROM mcr.microsoft.com/dotnet/sdk:5.0-buster-slim AS build-env
WORKDIR /app

COPY *.csproj ./
RUN dotnet restore

COPY . ./
RUN dotnet publish -c Release -o out

FROM mcr.microsoft.com/dotnet/aspnet:5.0-buster-slim
WORKDIR /app
COPY --from=build-env /app/out .
ENTRYPOINT ["dotnet", "myWebApp.dll"]