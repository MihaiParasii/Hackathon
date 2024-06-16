using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Cheburek999.Migrations
{
    /// <inheritdoc />
    public partial class Update4 : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<int>(
                name: "RamMemory",
                table: "Notebooks",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<int>(
                name: "RomMemory",
                table: "Notebooks",
                type: "int",
                nullable: false,
                defaultValue: 0);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "RamMemory",
                table: "Notebooks");

            migrationBuilder.DropColumn(
                name: "RomMemory",
                table: "Notebooks");
        }
    }
}
