//創建database
create database memproject;
use memproject;
//創建table
CREATE TABLE vocabulary_group (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(45) NULL,
  PRIMARY KEY (id))
ENGINE = InnoDB;
CREATE TABLE vocabulary (
  id INT NOT NULL AUTO_INCREMENT,
  vocabulary_group_id INT NOT NULL,
  name VARCHAR(45) NULL,
  meaning VARCHAR(45) NULL,
  days_reviewed FLOAT NULL,
  next_review_days FLOAT NULL,
  difficult FLOAT NULL,
  next_review_dates DATE NULL,
  lasttime_difficult INT NULL,
  PRIMARY KEY (id, vocabulary_group_id),
  INDEX fk_vocabulary_group_idx (vocabulary_group_id ASC) VISIBLE,
  CONSTRAINT fk_vocabulary_group
    FOREIGN KEY (vocabulary_group_id)
    REFERENCES memproject.vocabulary_group (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

//修改table格式
ALTER TABLE vocabulary
MODIFY days_reviewed DOUBLE  DEFAULT 1,
MODIFY next_review_days DOUBLE DEFAULT 1,
MODIFY difficult DOUBLE DEFAULT 2.5,
MODIFY next_review_dates DATE DEFAULT (CURDATE() ),
MODIFY lasttime_difficult INT DEFAULT 0;
Alter table vocabulary_group
ADD CONSTRAINT unique_column UNIQUE (name);

//創建第一個資料集(名稱) 編號自動增加
insert into vocabulary_group(name) values('abc');
//匯入資料格式(資料集編號,英文,中文)
insert into vocabulary(vocabulary_group_id,name,meaning) values(1,'apple','蘋果');


select * from vocabulary;
select * from vocabulary_group;
//測試歸零用
UPDATE `memproject`.`vocabulary` SET `days_reviewed` = '1', `next_review_days` = '1', `difficult` = '2.5', `next_review_dates` = '2024-09-10' WHERE (`id` = '1') and (`category_id` = '1');
UPDATE `memproject`.`vocabulary` SET `days_reviewed` = '1', `next_review_days` = '1', `difficult` = '2.5', `next_review_dates` = '2024-09-10' WHERE (`id` = '2') and (`category_id` = '1');
