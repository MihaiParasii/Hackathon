using Cheburek999.Data;
using Cheburek999.Models;
using Microsoft.AspNetCore.Mvc;

namespace Cheburek999.Controllers;

public class OperationSystemController(DavidContext context) : Controller
{
    public IActionResult Index()
    {
        return View();
    }

    public IActionResult AddOperationSystem()
    {
        return View();
    }

    public IActionResult AddOperationSystemToDb(string name)
    {
        OperationSystem operationSystem = new OperationSystem { Name = name };
        context.OperationSystems.Add(operationSystem);
        context.SaveChanges();
        return RedirectToAction("Index", "Home");
    }
}
