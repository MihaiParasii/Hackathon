using System.Diagnostics;
using Cheburek999.Data;
using Microsoft.AspNetCore.Mvc;
using Cheburek999.Models;

namespace Cheburek999.Controllers;

public class HomeController(ILogger<HomeController> logger, DavidContext context) : Controller
{
    private readonly ILogger<HomeController> _logger = logger;

    public IActionResult Index()
    {
        ViewData["companies"] = context.NotebookCompanies.ToList();
        ViewData["categories"] = context.Categories.ToList();
        return View();
    }

    public IActionResult Privacy()
    {
        return View();
    }

    [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
    public IActionResult Error()
    {
        return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
    }
}
