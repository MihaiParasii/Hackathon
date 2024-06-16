using Cheburek999.Data;
using Cheburek999.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Cheburek999.Controllers;

public class NotebookController(DavidContext context) : Controller
{
    public IActionResult Index(List<Notebook>? notebooks = null)
    {
        IEnumerable<int> cat = [-1];
        ViewData["cat"] = cat;
        return View(notebooks ?? context.Notebooks.Include(n => n.Company).ToList());
    }

    public IActionResult AddNotebook()
    {
        ViewData["notebookCompany"] = context.NotebookCompanies.ToList();
        ViewData["processor"] = context.Processors.ToList();
        ViewData["display"] = context.Displays.ToList();
        ViewData["category"] = context.Categories.ToList();

        return View(context.OperationSystems.ToList());
    }

    [HttpPost]
    public IActionResult AddNotebookToDb(string model, int batteryLife, int price, int operationSystemId,
        int notebookCompanyId, int processorId, int displayId, List<int> categoriesId, int ram, int rom)
    {
        List<NotebookCategory> foundedCategories = [];
        foundedCategories.AddRange(from id in categoriesId
            from contextCategory in context.Categories
            where contextCategory.Id == id
            select contextCategory);


        Notebook newNotebook = new Notebook
        {
            Model = model,
            BatteryLife = batteryLife,
            Price = price,
            OperationSystem = context.OperationSystems.ToList().First(system => system.Id == operationSystemId),
            Company = context.NotebookCompanies.ToList().First(company => company.Id == notebookCompanyId),
            Processor = context.Processors.ToList().First(processor => processor.Id == processorId),
            Display = context.Displays.ToList().First(display => display.Id == displayId),
            Categories = foundedCategories,
            RamMemory = ram,
            RomMemory = rom,
        };

        context.Notebooks.Add(newNotebook);
        context.SaveChanges();

        return RedirectToAction("Index", "Home");
    }

    [HttpGet]
    public IActionResult DetailedView(int id)
    {
        var list = context.Notebooks
            .Include(n => n.Company)
            .Include(n => n.Categories)
            .Include(n => n.Display)
            .Include(n => n.Processor)
            .Include(n => n.Processor.ProcessorCompany)
            .Include(n => n.OperationSystem)
            .ToList();

        foreach (Notebook n in list.Where(n => n.Id == id))
        {
            return View(n);
        }

        return View("NotebookNotFound");
    }

    [HttpPost]
    public IActionResult FilteringNotebooks(ICollection<int> manufacturesId, ICollection<int> selectedCategories,
        int batteryLife, string os, int screenSize, int priceRange)
    {
        int minPrice = 0;
        int maxPrice = 1000000;

        switch (priceRange)
        {
            case 1:
                maxPrice = 1000;
                break;
            case 2:
                minPrice = 1000;
                maxPrice = 1500;
                break;
            case 3:
                minPrice = 1500;
                maxPrice = 2000;
                break;
            case 4:
                minPrice = 2000;
                maxPrice = 100000;
                break;
        }

        int minBatteryLife = 0;
        int maxBatteryLife = 100;

        switch (batteryLife)
        {
            case 1:
                maxBatteryLife = 7;
                break;
            case 2:
                minBatteryLife = 7;
                maxBatteryLife = 12;
                break;
            case 3:
                minBatteryLife = 12;
                maxBatteryLife = 16;
                break;
            case 4:
                minBatteryLife = 16;
                maxBatteryLife = 100;
                break;
        }

        int minScreenSize = 0;
        int maxScreenSize = 100;

        switch (screenSize)
        {
            case 1:
                maxScreenSize = 14;
                break;
            case 2:
                minScreenSize = 14;
                maxScreenSize = 16;
                break;
            case 3:
                minScreenSize = 16;
                maxScreenSize = 100;
                break;
        }


        var list = context.Notebooks
            .Include(n => n.Company)
            .Include(n => n.Categories)
            .Include(n => n.Display)
            .Include(n => n.Processor)
            .Include(n => n.Processor.ProcessorCompany)
            .Include(n => n.OperationSystem)
            .ToList();

        List<Notebook> foundedNotebooks = (from n in list
            where n.Price >= minPrice && n.Price <= maxPrice
            where n.BatteryLife >= minBatteryLife && n.BatteryLife <= maxBatteryLife
            where n.Display.Diagonal >= minScreenSize && n.Display.Diagonal <= maxScreenSize
            where n.OperationSystem.Name == os
            from id in selectedCategories
            from category in n.Categories
            where category.Id == id
            from mId in manufacturesId
            where mId == n.Company.Id
            select n).ToList();

        return View("Index", foundedNotebooks);
    }
}
