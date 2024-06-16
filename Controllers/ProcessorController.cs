using Cheburek999.Data;
using Cheburek999.Models;
using Microsoft.AspNetCore.Mvc;

namespace Cheburek999.Controllers;

public class ProcessorController(DavidContext context) : Controller
{
    public IActionResult Index()
    {
        return View();
    }
    
    public IActionResult AddProcessor()
    {
        return View(context.ProcessorsCompany.ToList());
    }

    [HttpPost]
    public IActionResult AddProcessorToDb(string name, int coresCount, float frequency, int processorsCompanyId)
    {
        ProcessorCompany processorCompany = context.ProcessorsCompany.ToList()[0];

        foreach (var company in context.ProcessorsCompany.ToList().Where(company => company.Id == processorsCompanyId))
        {
            processorCompany = company;
            break;
        }

        Processor newProcessor = new Processor
        {
            Name = name,
            CoresCount = coresCount,
            Frequency = frequency,
            ProcessorCompany = processorCompany
        };

        context.Processors.Add(newProcessor);
        context.SaveChanges();
        
        return RedirectToAction("Index", "Home");
    }
}
