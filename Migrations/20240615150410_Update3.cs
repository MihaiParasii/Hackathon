using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Cheburek999.Migrations
{
    /// <inheritdoc />
    public partial class Update3 : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Notebooks_Categories_NotebookCategoryId",
                table: "Notebooks");

            migrationBuilder.DropIndex(
                name: "IX_Notebooks_NotebookCategoryId",
                table: "Notebooks");

            migrationBuilder.DropColumn(
                name: "NotebookCategoryId",
                table: "Notebooks");

            migrationBuilder.AddColumn<int>(
                name: "CategoryId",
                table: "Notebooks",
                type: "int",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.CreateIndex(
                name: "IX_Notebooks_CategoryId",
                table: "Notebooks",
                column: "CategoryId");

            migrationBuilder.AddForeignKey(
                name: "FK_Notebooks_Categories_CategoryId",
                table: "Notebooks",
                column: "CategoryId",
                principalTable: "Categories",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Notebooks_Categories_CategoryId",
                table: "Notebooks");

            migrationBuilder.DropIndex(
                name: "IX_Notebooks_CategoryId",
                table: "Notebooks");

            migrationBuilder.DropColumn(
                name: "CategoryId",
                table: "Notebooks");

            migrationBuilder.AddColumn<int>(
                name: "NotebookCategoryId",
                table: "Notebooks",
                type: "int",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_Notebooks_NotebookCategoryId",
                table: "Notebooks",
                column: "NotebookCategoryId");

            migrationBuilder.AddForeignKey(
                name: "FK_Notebooks_Categories_NotebookCategoryId",
                table: "Notebooks",
                column: "NotebookCategoryId",
                principalTable: "Categories",
                principalColumn: "Id");
        }
    }
}
