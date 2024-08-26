CREATE TRIGGER Update_Estantes_After_Insert2
AFTER INSERT ON Usuarios
FOR EACH ROW
BEGIN
    INSERT INTO Estantes (ID_Usuario, ID_Livro)
    SELECT Livros.Title, NEW.Name
    FROM Livros;
END