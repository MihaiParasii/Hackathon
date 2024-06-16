using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Cheburek999.Models;

public class Notebook
{
    [Key, DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; init; }

    [Required, MaxLength(30)] public required string Model { get; set; } = null!;
    [Required] public required OperationSystem OperationSystem { get; set; } = null!;
    [Required] public required NotebookCompany Company { get; set; } = null!;
    [Required] public required Processor Processor { get; set; } = null!;
    [Required] public required Display Display { get; set; } = null!;
    [Required] public required ICollection<NotebookCategory> Categories { get; set; } = null!;
    [Required] public required int BatteryLife { get; set; }
    [Required] public required int RamMemory { get; set; }
    [Required] public required int RomMemory { get; set; }
    [Required] public required float Price { get; set; }
}
