using Cheburek999.Data;
using Cheburek999.Models;
using Microsoft.AspNetCore.Mvc;

namespace Cheburek999.Controllers;

public class NotebookCompanyController(DavidContext context) : Controller
{
    public IActionResult Index()
    {
        return View();
    }
    
    public IActionResult AddNotebookCompany()
    {
        return View();
    }

    [HttpPost]
    public IActionResult AddNotebookCompanyToDb(string name)
    {
        NotebookCompany notebookCompany = new NotebookCompany
        {
            Name = name
        };
        context.NotebookCompanies.Add(notebookCompany);
        context.SaveChanges();
        return RedirectToAction("Index", "Home");
    }
}
