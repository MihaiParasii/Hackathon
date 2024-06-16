using Cheburek999.Data;
using Cheburek999.Models;
using Microsoft.AspNetCore.Mvc;

namespace Cheburek999.Controllers;

public class DisplayController(DavidContext context) : Controller
{
    public IActionResult Index()
    {
        return View();
    }

    public IActionResult AddDisplay()
    {
        return View();
    }

    [HttpPost]
    public IActionResult AddDisplayToDb(int pixelX, int pixelY, int refreshRate, int diagonal)
    {
        Display newDisplay = new Display
        {
            PixelsX = pixelX,
            PixelsY = pixelY,
            RefreshRate = refreshRate,
            Diagonal = diagonal
        };

        context.Displays.Add(newDisplay);
        context.SaveChanges();
        
        return RedirectToAction("Index", "Home");
    }
}
