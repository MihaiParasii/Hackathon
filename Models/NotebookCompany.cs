using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Cheburek999.Models;

public class NotebookCompany
{
    [Key, DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; init; }

    [Required] public string Name { get; set; } = null!;
    public ICollection<Notebook>? Notebooks { get; init; }
}
