using Cheburek999.Data;
using Cheburek999.Models;
using Microsoft.AspNetCore.Mvc;

namespace Cheburek999.Controllers;

public class NotebookCategoryController(DavidContext context) : Controller
{
    public IActionResult Index()
    {
        return View();
    }
    
    public IActionResult AddNotebookCategory()
    {
        return View();
    }

    [HttpPost]
    public IActionResult AddNotebookCategoryToDb(string name)
    {
        NotebookCategory notebookCategory = new NotebookCategory
        {
            Name = name
        };
        context.Categories.Add(notebookCategory);
        context.SaveChanges();
        return RedirectToAction("Index", "Home");
    }
}
