using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Cheburek999.Models;

public class NotebookCategory
{
    [Key, DatabaseGenerated(DatabaseGeneratedOption.Identity)]
    public int Id { get; set; }


    [Required] public string Name { get; set; } = null!;
    public ICollection<Notebook>? Notebooks { get; init; }

    public override string ToString()
    {
        return $"{Name}";
    }
}
