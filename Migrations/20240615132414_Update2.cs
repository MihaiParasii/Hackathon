using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Cheburek999.Migrations
{
    /// <inheritdoc />
    public partial class Update2 : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.RenameColumn(
                name: "CoreCount",
                table: "Processors",
                newName: "CoresCount");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.RenameColumn(
                name: "CoresCount",
                table: "Processors",
                newName: "CoreCount");
        }
    }
}
