using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Cheburek999.Models;

public class Processor
{
    [Key, DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    [Required] public required string Name { get; set; } = null!;
    [Required] public required int CoresCount { get; set; }
    [Required] public required float Frequency { get; set; }
    [Required] public ProcessorCompany ProcessorCompany { get; set; } = null!;
    [Required] public ICollection<Notebook>? Notebooks { get; set; }
    
    
    public override string ToString()
    {
        return $"{Name} {CoresCount} Cores, {Frequency} GHz";
    }
}
