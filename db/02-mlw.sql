-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: mariadb
-- Generation Time: Apr 23, 2025 at 02:19 PM
-- Server version: 11.7.2-MariaDB-ubu2404
-- PHP Version: 8.2.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";
use mlw;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `mlw`
--

-- --------------------------------------------------------

--
-- Table structure for table `action_type`
--

CREATE TABLE `action_type` (
  `type_id` int(11) NOT NULL,
  `type_name` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `action_type`
--

INSERT INTO `action_type` (`type_id`, `type_name`) VALUES
(3, 'Create'),
(6, 'Download'),
(2, 'New'),
(7, 'Recover'),
(4, 'Remove'),
(1, 'Search'),
(5, 'Update');

-- --------------------------------------------------------

--
-- Table structure for table `application`
--

CREATE TABLE `application` (
  `app_id` int(11) NOT NULL,
  `p_id` int(11) NOT NULL,
  `sep_id` int(11) NOT NULL,
  `app_name` varchar(32) NOT NULL,
  `svn_file` varchar(255) DEFAULT NULL,
  `template` varchar(63) DEFAULT NULL,
  `owner_id` int(11) NOT NULL,
  `create_time` date NOT NULL DEFAULT current_timestamp(),
  `update_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `application`
--

INSERT INTO `application` (`app_id`, `p_id`, `sep_id`, `app_name`, `svn_file`, `template`, `owner_id`, `create_time`, `update_time`) VALUES
(141, 1, 1, 'admin_test', 'http://172.16.4.11/test_svn_server/trunk/multilang/admin_test/', 'lang-en-US.js', 1, '2024-05-28', '0000-00-00 00:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `appstring_namespace`
--

CREATE TABLE `appstring_namespace` (
  `asn_id` int(11) NOT NULL,
  `app_id` int(11) NOT NULL,
  `str_id` int(11) NOT NULL,
  `namespace_id` int(11) NOT NULL,
  `deleted` int(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `appstring_namespace`
--

INSERT INTO `appstring_namespace` (`asn_id`, `app_id`, `str_id`, `namespace_id`, `deleted`) VALUES
(25875, 141, 16072, 12450, 0);

-- --------------------------------------------------------

--
-- Table structure for table `language`
--

CREATE TABLE `language` (
  `lang_id` int(11) NOT NULL,
  `lang_tag` varchar(15) NOT NULL,
  `lang_name` varchar(31) NOT NULL,
  `chinese_name` varchar(64) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `language`
--

INSERT INTO `language` (`lang_id`, `lang_tag`, `lang_name`, `chinese_name`) VALUES
(1, 'en-US', 'English', '英文'),
(2, 'zh-TW', 'Traditional Chinese', '繁體中文'),
(3, 'zh-CN', 'Simplified Chinese', '簡體中文'),
(4, 'de-DE', 'German', '德文'),
(5, 'ja-JP', 'Japanese', '日文'),
(6, 'it-IT', 'Italian', '義大利文'),
(7, 'fr-FR', 'French', '法文'),
(8, 'nl-NL', 'Dutch', '荷蘭文'),
(9, 'ru-RU', 'Russian', '俄文'),
(10, 'ko-KR', 'Korean', '韓文'),
(11, 'pl', 'Polish', '波蘭文'),
(12, 'cs', 'Czech', '捷克文'),
(13, 'sv', 'Svenska', '瑞典文'),
(14, 'da', 'Dansk', '丹麥文'),
(15, 'no', 'Norsk', '挪威文'),
(16, 'fi', 'Suomi', '芬蘭文'),
(17, 'pt', 'Portugal', '葡萄牙文'),
(18, 'es', 'Spanish', '西班牙文'),
(19, 'hu', 'Hungarian', '匈牙利文'),
(20, 'tr', 'Turkish', '土耳其文'),
(21, 'es-latino', 'Spanish -  Latino America', '西班牙文 - 拉丁美洲'),
(22, 'th', 'Thai', '泰文');

-- --------------------------------------------------------

--
-- Table structure for table `log`
--

CREATE TABLE `log` (
  `log_id` int(11) NOT NULL,
  `u_id` int(11) NOT NULL,
  `type_id` int(2) NOT NULL,
  `log` text NOT NULL,
  `time` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

--
-- Dumping data for table `log`
--

INSERT INTO `log` (`log_id`, `u_id`, `type_id`, `log`, `time`) VALUES
(1, 1, 3, 'App: admin_test <br>Namespace_id: 12450 <br>Namespace: _AS_STRINGS.LOGIN.FRIDAY <br>StringID: 16072', '2025-04-23 14:17:03'),
(3, 1, 4, 'Asn_id: 25875<br>App: admin_test <br>String: Friday <br>Namespace: _AS_STRINGS.LOGIN.FRIDAY', '2025-04-23 14:18:16'),
(4, 1, 7, 'StringID: 16072 <br>Lang: Traditional Chinese <br>Before_recover: 週五123 <br>After_recover: 週五', '2025-04-23 14:18:57'),
(5, 1, 5, 'StringID: 16072 <br>Language: Traditional Chinese <br>Old_content: 週五 <br>New_content: 週五1', '2025-04-23 14:19:03');

-- --------------------------------------------------------

--
-- Table structure for table `namespace`
--

CREATE TABLE `namespace` (
  `namespace_id` int(11) NOT NULL,
  `name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `namespace`
--

INSERT INTO `namespace` (`namespace_id`, `name`) VALUES
(12450, '_AS_STRINGS.LOGIN.FRIDAY');

-- --------------------------------------------------------

--
-- Table structure for table `platform`
--

CREATE TABLE `platform` (
  `p_id` int(11) NOT NULL,
  `p_name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `platform`
--

INSERT INTO `platform` (`p_id`, `p_name`) VALUES
(4, 'Android'),
(6, 'Chrome'),
(7, 'Firefox'),
(5, 'iOS'),
(3, 'Mac'),
(8, 'Official Site'),
(9, 'Official Site Database'),
(1, 'WebUI'),
(2, 'Win');

-- --------------------------------------------------------

--
-- Table structure for table `proofread_log`
--

CREATE TABLE `proofread_log` (
  `log_id` int(11) NOT NULL,
  `u_id` int(11) NOT NULL,
  `action` int(11) NOT NULL,
  `ps_id` int(11) NOT NULL,
  `old_string` text DEFAULT NULL,
  `new_string` text DEFAULT NULL,
  `time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `proofread_project`
--

CREATE TABLE `proofread_project` (
  `project_id` int(11) NOT NULL,
  `project_name` text NOT NULL,
  `spec_link` text NOT NULL,
  `person_in_charge` int(11) NOT NULL,
  `reviewer` int(11) DEFAULT NULL,
  `deleted` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `proofread_string`
--

CREATE TABLE `proofread_string` (
  `ps_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `string` text NOT NULL,
  `deleted` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `separator`
--

CREATE TABLE `separator` (
  `sep_id` int(11) NOT NULL,
  `type` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `separator`
--

INSERT INTO `separator` (`sep_id`, `type`) VALUES
(2, '--'),
(3, '---'),
(1, '.');

-- --------------------------------------------------------

--
-- Table structure for table `string`
--

CREATE TABLE `string` (
  `str_id` int(11) NOT NULL,
  `postfix` varchar(255) NOT NULL,
  `note` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `string`
--

INSERT INTO `string` (`str_id`, `postfix`, `note`) VALUES
(16072, 'FRIDAY', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `string_language`
--

CREATE TABLE `string_language` (
  `sl_id` int(11) NOT NULL,
  `str_id` int(11) NOT NULL,
  `lang_id` int(11) NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `string_language`
--

INSERT INTO `string_language` (`sl_id`, `str_id`, `lang_id`, `content`) VALUES
(22155, 16072, 1, 'Friday'),
(22156, 16072, 2, '週五1'),
(22157, 16072, 3, '星期五'),
(22158, 16072, 4, 'Freitag'),
(22159, 16072, 5, '金曜日'),
(22160, 16072, 6, 'Venerdì'),
(22161, 16072, 7, 'Vendredi'),
(22162, 16072, 8, 'vrijdag'),
(22163, 16072, 9, 'Пятница'),
(22164, 16072, 10, '금요일'),
(22165, 16072, 11, 'Piątek'),
(22166, 16072, 12, 'Pátek'),
(22167, 16072, 13, 'Fredag'),
(22168, 16072, 14, 'Fredag '),
(22169, 16072, 15, 'Fredag'),
(22170, 16072, 16, 'Perjantai'),
(22171, 16072, 17, 'Sexta feira'),
(22172, 16072, 18, 'Viernes'),
(22173, 16072, 19, 'Péntek'),
(22174, 16072, 20, 'Cuma'),
(22175, 16072, 21, 'Viernes'),
(22176, 16072, 22, 'ศุกร์');

--
-- Triggers `string_language`
--
DELIMITER $$
CREATE TRIGGER `update_string` AFTER UPDATE ON `string_language` FOR EACH ROW BEGIN
                    INSERT INTO `string_update_log` (`lang_id`, `str_id`, `old_value`, `new_value`, `update_by`) 
                    VALUES (new.lang_id, new.str_id, old.content, new.content, 'system');
                END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Stand-in structure for view `string_mapping`
-- (See below for the actual view)
--
CREATE TABLE `string_mapping` (
`p_id` int(11)
,`p_name` varchar(255)
,`app_id` int(11)
,`app_name` varchar(32)
,`namespace_id` int(11)
,`namespace` varchar(200)
,`str_id` int(11)
,`en-US` text
,`zh-TW` text
,`zh-CN` text
,`de-DE` text
,`ja-JP` text
,`it-IT` text
,`fr-FR` text
,`nl-NL` text
,`ru-RU` text
,`ko-KR` text
,`pl` text
,`cs` text
,`sv` text
,`da` text
,`no` text
,`fi` text
,`pt` text
,`es` text
,`hu` text
,`tr` text
,`es-latino` text
,`th` text
);

-- --------------------------------------------------------

--
-- Table structure for table `string_update_log`
--

CREATE TABLE `string_update_log` (
  `l_id` int(11) NOT NULL,
  `lang_id` int(11) NOT NULL,
  `str_id` int(11) NOT NULL,
  `old_value` text DEFAULT NULL,
  `new_value` text NOT NULL,
  `deleted` tinyint(1) NOT NULL DEFAULT 0,
  `updated_time` timestamp NOT NULL DEFAULT current_timestamp(),
  `update_by` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `string_update_log`
--

INSERT INTO `string_update_log` (`l_id`, `lang_id`, `str_id`, `old_value`, `new_value`, `deleted`, `updated_time`, `update_by`) VALUES
(1, 2, 16072, '週五', '週五123', 1, '2025-04-23 14:08:24', 'system'),
(2, 2, 16072, '週五123', '週五1234', 1, '2025-04-23 14:08:36', 'system'),
(3, 2, 16072, '週五', '週五1', 0, '2025-04-23 14:19:03', 'system');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `u_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `deleted` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`u_id`, `name`, `password`, `deleted`) VALUES
(1, 'admin', '$2b$12$3TdZAuTQZ.gYAqL6xJMreeP2RLAsCyyNym6N0vWfbm/rXcfV58DwW', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `action_type`
--
ALTER TABLE `action_type`
  ADD PRIMARY KEY (`type_id`),
  ADD UNIQUE KEY `type_name` (`type_name`);

--
-- Indexes for table `application`
--
ALTER TABLE `application`
  ADD PRIMARY KEY (`app_id`),
  ADD KEY `p_id` (`p_id`),
  ADD KEY `sep_id` (`sep_id`),
  ADD KEY `owner_id` (`owner_id`);

--
-- Indexes for table `appstring_namespace`
--
ALTER TABLE `appstring_namespace`
  ADD PRIMARY KEY (`asn_id`),
  ADD KEY `app_id` (`app_id`),
  ADD KEY `str_id` (`str_id`),
  ADD KEY `namespace_id` (`namespace_id`);

--
-- Indexes for table `language`
--
ALTER TABLE `language`
  ADD PRIMARY KEY (`lang_id`),
  ADD UNIQUE KEY `lang_name` (`lang_name`);

--
-- Indexes for table `log`
--
ALTER TABLE `log`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `u_id` (`u_id`),
  ADD KEY `type_id` (`type_id`);

--
-- Indexes for table `namespace`
--
ALTER TABLE `namespace`
  ADD PRIMARY KEY (`namespace_id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `platform`
--
ALTER TABLE `platform`
  ADD PRIMARY KEY (`p_id`),
  ADD UNIQUE KEY `p_name` (`p_name`);

--
-- Indexes for table `proofread_log`
--
ALTER TABLE `proofread_log`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `ps_id` (`ps_id`),
  ADD KEY `user` (`u_id`),
  ADD KEY `action` (`action`);

--
-- Indexes for table `proofread_project`
--
ALTER TABLE `proofread_project`
  ADD PRIMARY KEY (`project_id`),
  ADD KEY `person_in_charge` (`person_in_charge`),
  ADD KEY `reviewer` (`reviewer`);

--
-- Indexes for table `proofread_string`
--
ALTER TABLE `proofread_string`
  ADD PRIMARY KEY (`ps_id`),
  ADD KEY `project_id` (`project_id`);

--
-- Indexes for table `separator`
--
ALTER TABLE `separator`
  ADD PRIMARY KEY (`sep_id`),
  ADD UNIQUE KEY `type` (`type`);

--
-- Indexes for table `string`
--
ALTER TABLE `string`
  ADD PRIMARY KEY (`str_id`);

--
-- Indexes for table `string_language`
--
ALTER TABLE `string_language`
  ADD PRIMARY KEY (`sl_id`),
  ADD KEY `str_id` (`str_id`),
  ADD KEY `lang_id` (`lang_id`);

--
-- Indexes for table `string_update_log`
--
ALTER TABLE `string_update_log`
  ADD PRIMARY KEY (`l_id`),
  ADD KEY `lang_id` (`lang_id`),
  ADD KEY `string_id` (`str_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`u_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `action_type`
--
ALTER TABLE `action_type`
  MODIFY `type_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `application`
--
ALTER TABLE `application`
  MODIFY `app_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=149;

--
-- AUTO_INCREMENT for table `appstring_namespace`
--
ALTER TABLE `appstring_namespace`
  MODIFY `asn_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25876;

--
-- AUTO_INCREMENT for table `language`
--
ALTER TABLE `language`
  MODIFY `lang_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT for table `log`
--
ALTER TABLE `log`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `namespace`
--
ALTER TABLE `namespace`
  MODIFY `namespace_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20903;

--
-- AUTO_INCREMENT for table `platform`
--
ALTER TABLE `platform`
  MODIFY `p_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `proofread_log`
--
ALTER TABLE `proofread_log`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `proofread_project`
--
ALTER TABLE `proofread_project`
  MODIFY `project_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `proofread_string`
--
ALTER TABLE `proofread_string`
  MODIFY `ps_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `separator`
--
ALTER TABLE `separator`
  MODIFY `sep_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `string`
--
ALTER TABLE `string`
  MODIFY `str_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31015;

--
-- AUTO_INCREMENT for table `string_language`
--
ALTER TABLE `string_language`
  MODIFY `sl_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=286957;

--
-- AUTO_INCREMENT for table `string_update_log`
--
ALTER TABLE `string_update_log`
  MODIFY `l_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `u_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

-- --------------------------------------------------------

--
-- Structure for view `string_mapping`
--
DROP TABLE IF EXISTS `string_mapping`;

CREATE ALGORITHM=UNDEFINED DEFINER=`admin`@`%` SQL SECURITY DEFINER VIEW `string_mapping`  AS SELECT `p`.`p_id` AS `p_id`, `p`.`p_name` AS `p_name`, `a`.`app_id` AS `app_id`, `a`.`app_name` AS `app_name`, `n`.`namespace_id` AS `namespace_id`, `n`.`name` AS `namespace`, `s`.`str_id` AS `str_id`, `sl_en`.`content` AS `en-US`, `sl_zh_tw`.`content` AS `zh-TW`, `sl_zh_cn`.`content` AS `zh-CN`, `sl_de`.`content` AS `de-DE`, `sl_ja`.`content` AS `ja-JP`, `sl_it`.`content` AS `it-IT`, `sl_fr`.`content` AS `fr-FR`, `sl_nl`.`content` AS `nl-NL`, `sl_ru`.`content` AS `ru-RU`, `sl_ko`.`content` AS `ko-KR`, `sl_pl`.`content` AS `pl`, `sl_cs`.`content` AS `cs`, `sl_sv`.`content` AS `sv`, `sl_da`.`content` AS `da`, `sl_no`.`content` AS `no`, `sl_fi`.`content` AS `fi`, `sl_pt`.`content` AS `pt`, `sl_es`.`content` AS `es`, `sl_hu`.`content` AS `hu`, `sl_tr`.`content` AS `tr`, `sl_es_latino`.`content` AS `es-latino`, `sl_th`.`content` AS `th` FROM ((((((((((((((((((((((((((`appstring_namespace` `asn` join `namespace` `n` on(`asn`.`namespace_id` = `n`.`namespace_id`)) join `application` `a` on(`asn`.`app_id` = `a`.`app_id`)) left join `platform` `p` on(`a`.`p_id` = `p`.`p_id`)) left join `string` `s` on(`asn`.`str_id` = `s`.`str_id`)) left join `string_language` `sl_en` on(`sl_en`.`str_id` = `s`.`str_id` and `sl_en`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'en-US'))) left join `string_language` `sl_zh_tw` on(`sl_zh_tw`.`str_id` = `s`.`str_id` and `sl_zh_tw`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'zh-TW'))) left join `string_language` `sl_zh_cn` on(`sl_zh_cn`.`str_id` = `s`.`str_id` and `sl_zh_cn`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'zh-CN'))) left join `string_language` `sl_de` on(`sl_de`.`str_id` = `s`.`str_id` and `sl_de`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'de-DE'))) left join `string_language` `sl_ja` on(`sl_ja`.`str_id` = `s`.`str_id` and `sl_ja`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'ja-JP'))) left join `string_language` `sl_it` on(`sl_it`.`str_id` = `s`.`str_id` and `sl_it`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'it-IT'))) left join `string_language` `sl_fr` on(`sl_fr`.`str_id` = `s`.`str_id` and `sl_fr`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'fr-FR'))) left join `string_language` `sl_nl` on(`sl_nl`.`str_id` = `s`.`str_id` and `sl_nl`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'nl-NL'))) left join `string_language` `sl_ru` on(`sl_ru`.`str_id` = `s`.`str_id` and `sl_ru`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'ru-RU'))) left join `string_language` `sl_ko` on(`sl_ko`.`str_id` = `s`.`str_id` and `sl_ko`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'ko-KR'))) left join `string_language` `sl_pl` on(`sl_pl`.`str_id` = `s`.`str_id` and `sl_pl`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'pl'))) left join `string_language` `sl_cs` on(`sl_cs`.`str_id` = `s`.`str_id` and `sl_cs`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'cs'))) left join `string_language` `sl_sv` on(`sl_sv`.`str_id` = `s`.`str_id` and `sl_sv`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'sv'))) left join `string_language` `sl_da` on(`sl_da`.`str_id` = `s`.`str_id` and `sl_da`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'da'))) left join `string_language` `sl_no` on(`sl_no`.`str_id` = `s`.`str_id` and `sl_no`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'no'))) left join `string_language` `sl_fi` on(`sl_fi`.`str_id` = `s`.`str_id` and `sl_fi`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'fi'))) left join `string_language` `sl_pt` on(`sl_pt`.`str_id` = `s`.`str_id` and `sl_pt`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'pt'))) left join `string_language` `sl_es` on(`sl_es`.`str_id` = `s`.`str_id` and `sl_es`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'es'))) left join `string_language` `sl_hu` on(`sl_hu`.`str_id` = `s`.`str_id` and `sl_hu`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'hu'))) left join `string_language` `sl_tr` on(`sl_tr`.`str_id` = `s`.`str_id` and `sl_tr`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'tr'))) left join `string_language` `sl_es_latino` on(`sl_es_latino`.`str_id` = `s`.`str_id` and `sl_es_latino`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'es-latino'))) left join `string_language` `sl_th` on(`sl_th`.`str_id` = `s`.`str_id` and `sl_th`.`lang_id` = (select `language`.`lang_id` from `language` where `language`.`lang_tag` = 'th'))) ;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `application`
--
ALTER TABLE `application`
  ADD CONSTRAINT `application_ibfk_1` FOREIGN KEY (`p_id`) REFERENCES `platform` (`p_id`),
  ADD CONSTRAINT `application_ibfk_2` FOREIGN KEY (`sep_id`) REFERENCES `separator` (`sep_id`),
  ADD CONSTRAINT `application_ibfk_3` FOREIGN KEY (`owner_id`) REFERENCES `user` (`u_id`);

--
-- Constraints for table `appstring_namespace`
--
ALTER TABLE `appstring_namespace`
  ADD CONSTRAINT `appstring_namespace_ibfk_1` FOREIGN KEY (`app_id`) REFERENCES `application` (`app_id`),
  ADD CONSTRAINT `appstring_namespace_ibfk_2` FOREIGN KEY (`str_id`) REFERENCES `string` (`str_id`),
  ADD CONSTRAINT `appstring_namespace_ibfk_3` FOREIGN KEY (`namespace_id`) REFERENCES `namespace` (`namespace_id`);

--
-- Constraints for table `log`
--
ALTER TABLE `log`
  ADD CONSTRAINT `log_ibfk_1` FOREIGN KEY (`u_id`) REFERENCES `user` (`u_id`),
  ADD CONSTRAINT `log_ibfk_2` FOREIGN KEY (`type_id`) REFERENCES `action_type` (`type_id`);

--
-- Constraints for table `proofread_log`
--
ALTER TABLE `proofread_log`
  ADD CONSTRAINT `proofread_log_ibfk_1` FOREIGN KEY (`ps_id`) REFERENCES `proofread_string` (`ps_id`),
  ADD CONSTRAINT `proofread_log_ibfk_2` FOREIGN KEY (`u_id`) REFERENCES `user` (`u_id`),
  ADD CONSTRAINT `proofread_log_ibfk_3` FOREIGN KEY (`action`) REFERENCES `action_type` (`type_id`);

--
-- Constraints for table `proofread_project`
--
ALTER TABLE `proofread_project`
  ADD CONSTRAINT `proofread_project_ibfk_1` FOREIGN KEY (`person_in_charge`) REFERENCES `user` (`u_id`),
  ADD CONSTRAINT `proofread_project_ibfk_2` FOREIGN KEY (`reviewer`) REFERENCES `user` (`u_id`);

--
-- Constraints for table `proofread_string`
--
ALTER TABLE `proofread_string`
  ADD CONSTRAINT `proofread_string_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `proofread_project` (`project_id`);

--
-- Constraints for table `string_language`
--
ALTER TABLE `string_language`
  ADD CONSTRAINT `string_language_ibfk_1` FOREIGN KEY (`str_id`) REFERENCES `string` (`str_id`),
  ADD CONSTRAINT `string_language_ibfk_2` FOREIGN KEY (`lang_id`) REFERENCES `language` (`lang_id`);

--
-- Constraints for table `string_update_log`
--
ALTER TABLE `string_update_log`
  ADD CONSTRAINT `string_update_log_ibfk_1` FOREIGN KEY (`lang_id`) REFERENCES `language` (`lang_id`),
  ADD CONSTRAINT `string_update_log_ibfk_2` FOREIGN KEY (`str_id`) REFERENCES `string_language` (`str_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
