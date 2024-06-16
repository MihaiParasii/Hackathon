using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Cheburek999.Models;

public class Display
{
    [Key, DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    [Required] public required int PixelsX { get; set; }
    [Required] public required int PixelsY { get; set; }
    [Required] public required float Diagonal { get; set; }
    [Required] public required int RefreshRate { get; set; }
    [Required] public ICollection<Notebook>? Notebooks { get; set; }

    public override string ToString()
    {
        return $"{PixelsY}x{PixelsX}, {Diagonal}'', {RefreshRate}";
        
    }
}
