using Cheburek999.Data;
using Cheburek999.Models;
using Microsoft.AspNetCore.Mvc;

namespace Cheburek999.Controllers;

public class ProcessorCompanyController(DavidContext context) : Controller
{
    public IActionResult Index()
    {
        return View();
    }
    
    public IActionResult AddProcessorCompany()
    {
        return View();
    }

    [HttpPost]
    public IActionResult AddProcessorCompanyToDb(string name)
    {
        ProcessorCompany processorCompany = new ProcessorCompany
        {
            Name = name
        };
        context.ProcessorsCompany.Add(processorCompany);
        context.SaveChanges();
        return RedirectToAction("Index", "Home");
    }
}
