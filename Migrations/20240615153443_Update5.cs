using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace Cheburek999.Migrations
{
    /// <inheritdoc />
    public partial class Update5 : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
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

            migrationBuilder.CreateTable(
                name: "NotebookNotebookCategory",
                columns: table => new
                {
                    CategoriesId = table.Column<int>(type: "int", nullable: false),
                    NotebooksId = table.Column<int>(type: "int", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_NotebookNotebookCategory", x => new { x.CategoriesId, x.NotebooksId });
                    table.ForeignKey(
                        name: "FK_NotebookNotebookCategory_Categories_CategoriesId",
                        column: x => x.CategoriesId,
                        principalTable: "Categories",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_NotebookNotebookCategory_Notebooks_NotebooksId",
                        column: x => x.NotebooksId,
                        principalTable: "Notebooks",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                })
                .Annotation("MySql:CharSet", "utf8mb4");

            migrationBuilder.CreateIndex(
                name: "IX_NotebookNotebookCategory_NotebooksId",
                table: "NotebookNotebookCategory",
                column: "NotebooksId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "NotebookNotebookCategory");

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
    }
}
