/**
 * generate-nav.js
 * Скрипт для автоматического создания nav.adoc файла для модуля Antora
 * на основе существующей файловой структуры.
 */

const fs = require('fs');
const path = require('path');

// Конфигурация
const config = {
  // Корневая директория модуля, относительно места запуска скрипта
  // Обычно это modules/MODULE_NAME
  modulePath: './docs/modules/ctvision',
  
  // Путь к директории pages относительно modulePath
  pagesDir: 'pages',
  
  // Выходной файл nav.adoc
  outputNavFile: 'nav.adoc',
  
  // Расширения файлов, которые нужно включить в навигацию
  includedExtensions: ['.adoc'],
  
  // Файлы, которые нужно исключить из навигации
  excludedFiles: ['index.adoc', 'README.adoc'],
  
  // Глубина вложенности навигации (0 - без ограничений)
  maxDepth: 0,
  
  // Заголовок для nav.adoc
  navTitle: 'CT Vision',
};

/**
 * Получает заголовок из AsciiDoc файла
 * @param {string} filePath - Путь к файлу
 * @return {string} - Заголовок или имя файла без расширения, если заголовок не найден
 */
function getTitleFromFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    // Ищем заголовок в формате "= Title"
    const titleMatch = content.match(/^=\s+(.+)$/m);
    if (titleMatch && titleMatch[1]) {
      return titleMatch[1].trim();
    }
    
    // Возвращаем имя файла без расширения, если заголовок не найден
    return path.basename(filePath, path.extname(filePath));
  } catch (error) {
    console.error(`Ошибка при чтении файла ${filePath}:`, error);
    return path.basename(filePath, path.extname(filePath));
  }
}

/**
 * Генерирует элементы навигации из директории
 * @param {string} dirPath - Путь к директории
 * @param {number} level - Текущий уровень вложенности
 * @param {string} relativePath - Относительный путь для ссылок
 * @return {string} - Строка с элементами навигации в формате AsciiDoc
 */
function generateNavItems(dirPath, level = 0, relativePath = '') {
  if (config.maxDepth > 0 && level > config.maxDepth) {
    return '';
  }
  
  let navItems = '';
  const indentation = '*'.repeat(level + 1) + ' ';
  
  // Получаем все файлы и директории в текущей директории
  const items = fs.readdirSync(dirPath, { withFileTypes: true });
  
  // Сортируем элементы: сначала директории, потом файлы
  const sortedItems = [
    ...items.filter(item => item.isDirectory()),
    ...items.filter(item => item.isFile())
  ];
  
  // Обрабатываем все элементы
  for (const item of sortedItems) {
    const itemPath = path.join(dirPath, item.name);
    const itemRelativePath = path.join(relativePath, item.name);
    
    if (item.isDirectory()) {
      // Проверяем, есть ли index.adoc в директории
      const indexPath = path.join(itemPath, 'index.adoc');
      const hasIndex = fs.existsSync(indexPath);
      
      // Проверяем, есть ли файлы или директории внутри текущей директории
      const subItems = fs.readdirSync(itemPath, { withFileTypes: true });
      const hasContent = subItems.length > 0;
      
      if (hasContent) {
        let dirTitle = item.name.charAt(0).toUpperCase() + item.name.slice(1).replace(/-/g, ' ');
        
        if (hasIndex) {
          dirTitle = getTitleFromFile(indexPath);
          // Добавляем директорию как ссылку на index.adoc
          navItems += `${indentation}xref:${path.join(itemRelativePath, 'index.adoc')}[${dirTitle}]\n`;
        } else {
          // Добавляем директорию как заголовок
          navItems += `${indentation}${dirTitle}\n`;
        }
        
        // Рекурсивно обрабатываем содержимое директории
        const subNav = generateNavItems(itemPath, level + 1, itemRelativePath);
        if (subNav) {
          navItems += subNav;
        }
      }
    } 
    else if (item.isFile()) {
      // Проверяем, что это adoc файл и не в списке исключений
      if (config.includedExtensions.includes(path.extname(item.name)) && 
          !config.excludedFiles.includes(item.name)) {
        
        const title = getTitleFromFile(itemPath);
        // Оставляем расширение .adoc для правильных ссылок
        const link = itemRelativePath;
        
        navItems += `${indentation}xref:${link}[${title}]\n`;
      }
    }
  }
  
  return navItems;
}

/**
 * Генерирует содержимое nav.adoc файла
 * @return {string} - Содержимое nav.adoc
 */
function generateNav() {
  const pagesPath = path.join(config.modulePath, config.pagesDir);
  
  // Формат для стандарта Antora
  let navContent = '';
  
  // Если указан заголовок, добавляем его
  if (config.navTitle) {
    navContent += `.${config.navTitle}\n`;
  }
  
  // Добавляем элементы навигации
  navContent += generateNavItems(pagesPath);
  
  return navContent;
}

/**
 * Основная функция
 */
function main() {
  try {
    // Проверяем существование директорий
    const pagesPath = path.join(config.modulePath, config.pagesDir);
    if (!fs.existsSync(pagesPath)) {
      console.error(`Директория ${pagesPath} не найдена!`);
      process.exit(1);
    }
    
    // Генерируем содержимое nav.adoc
    const navContent = generateNav();
    
    // Записываем в файл
    const outputPath = path.join(config.modulePath, config.outputNavFile);
    fs.writeFileSync(outputPath, navContent, 'utf8');
    
    console.log(`Файл nav.adoc успешно создан: ${outputPath}`);
  } catch (error) {
    console.error('Ошибка при генерации nav.adoc:', error);
    process.exit(1);
  }
}

// Запускаем основную функцию
main();