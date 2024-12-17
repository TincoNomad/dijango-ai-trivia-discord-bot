-- Dar todos los permisos al usuario admin
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' WITH GRANT OPTION;

-- Dar permisos específicos para la base de datos de pruebas
GRANT ALL PRIVILEGES ON `test_trivia_db`.* TO 'admin'@'%';
GRANT ALL PRIVILEGES ON `trivia_db`.* TO 'admin'@'%';

-- Permitir crear bases de datos
GRANT CREATE ON *.* TO 'admin'@'%';

FLUSH PRIVILEGES;
