using Cheburek999.Models;
using Microsoft.EntityFrameworkCore;


namespace Cheburek999.Data;

public class DavidContext : DbContext
{
    public DbSet<Notebook> Notebooks { get; init; }
    public DbSet<Display> Displays { get; init; }
    public DbSet<NotebookCategory> Categories { get; init; }
    public DbSet<NotebookCompany> NotebookCompanies { get; init; }
    public DbSet<OperationSystem> OperationSystems { get; init; }
    public DbSet<Processor> Processors { get; init; }
    public DbSet<ProcessorCompany> ProcessorsCompany { get; init; }


    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        base.OnConfiguring(optionsBuilder);
        var serverVersion = new MySqlServerVersion(new Version(8, 3, 0));
        const string connectionString = "server=localhost;user=root;password=;database=cheburek999";
        optionsBuilder.UseMySql(connectionString, serverVersion);
    }
}
