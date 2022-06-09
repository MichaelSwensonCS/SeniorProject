using CliWrap;
using Groove.DataLayer;
using Groove.Objects.Configuration;
using Groove.Objects.Interfaces;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Recommender
{
    public class PyRecommender : BackgroundService
    {
        private readonly ILogger<PyRecommender> _logger;
        private readonly IRecommenderChannel _recommenderChannel;
        private readonly IServiceProvider _services;

        public PyRecommender(ILogger<PyRecommender> logger, IRecommenderChannel recommenderChannel, IServiceProvider services)
        {
            _logger = logger;
            _recommenderChannel = recommenderChannel;
            _services = services;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Recommender started at: {time}", DateTimeOffset.Now);
            while (!stoppingToken.IsCancellationRequested)
            {
                await foreach (var data in _recommenderChannel.ReadAllAsync())
                {
                    var stdOutBuffer = new StringBuilder();
                    var stdErrBuffer = new StringBuilder();
                    using (var scope = _services.CreateScope())
                    {
                        var sp = scope.ServiceProvider;
                        var userService = sp.GetRequiredService<IUserService>();
                        var s = sp.GetRequiredService<IOptions<RecommenderServiceOpts>>()?.Value;
                        var db = sp.GetRequiredService<DataContext>();

                        await userService.UpdateGettingRecs(data.AppUserId, true);
                        var result = await Cli.Wrap("python3")
                            .WithArguments(args => args
                                .Add("recommender.py")
                                .Add(s.Server)
                                .Add(s.Port)
                                .Add(s.Database)
                                .Add(s.User)
                                .Add(s.Password)
                                .Add(data.RecommendationType)
                                .Add(data.AppUserId))
                            .WithValidation(CommandResultValidation.None)
                            .WithStandardOutputPipe(PipeTarget.ToStringBuilder(stdOutBuffer))
                            .WithStandardErrorPipe(PipeTarget.ToStringBuilder(stdErrBuffer))
                            .ExecuteAsync();

                        var stdOut = stdOutBuffer.ToString();
                        var stdErr = stdErrBuffer.ToString();

                        if (!string.IsNullOrEmpty(stdErr))
                        {
                            _logger.LogError(stdErr);
                        }
                        if (!string.IsNullOrEmpty(stdOut))
                        {
                            _logger.LogInformation(stdOut);
                        }

                        await userService.UpdateGettingRecs(data.AppUserId, false);
                    }
                }
            }
        }
    }
}
