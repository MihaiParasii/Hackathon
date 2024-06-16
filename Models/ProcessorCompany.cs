using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Cheburek999.Models;

public class ProcessorCompany
{
    [Key, DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }

    [Required] public required string Name { get; set; } = null!;
    public List<Processor>? Processors { get; set; } = null!;
}
