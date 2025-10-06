--
-- PostgreSQL database dump
--

\restrict 8oHFQR1A9pYwhzD79YQBEad58lWHt4XLluLhucGsHg6V8GN49K7LkUzy9jjR9VO

-- Dumped from database version 14.18 (Homebrew)
-- Dumped by pg_dump version 14.19 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: company_email_mapping; Type: TABLE DATA; Schema: public; Owner: bill_user
--

INSERT INTO public.company_email_mapping (id, company_name, sender_email, created_at) VALUES (2, 'PRL', 'prl@credentia.biz', NULL);


--
-- Data for Name: nominal_code; Type: TABLE DATA; Schema: public; Owner: bill_user
--

INSERT INTO public.nominal_code (id, code, object_name) VALUES (143, '0010', 'Freehold Property');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (144, '0011', 'Freehold Prop Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (145, '0012', 'Leasehold Property');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (146, '0013', 'Leasehold Prop Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (147, '0014', 'Property');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (148, '0015', 'Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (149, '0020', 'Plant and Machinery');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (150, '0021', 'Plant/Machinery Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (151, '0030', 'Office Equipment');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (152, '0031', 'Office Equipment Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (153, '0040', 'Furniture and Fixtures');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (154, '0041', 'Furniture/Fixture Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (155, '0050', 'Motor Vehicles');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (156, '0051', 'Motor Vehicles Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (157, '0055', 'Investment - Dearnside Motor Co');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (158, '0056', 'Investment in joint venture - PAIL');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (159, '0057', 'Investment in subsidiary');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (160, '0058', 'Investment- JBros (Investments) Ltd.');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (161, '0060', 'Others');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (162, '0061', 'Others Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (163, '0062', 'Intangible Assets');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (164, '0063', 'intangible Assets Depreciation-(sathees)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (165, '0064', 'Improvement of Assets');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (166, '0065', 'Improvement of Assets- Accumulated Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (167, '0070', 'Delph & Saxon Prelim');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (168, '0080', 'Professional Fees (Capitalization)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (169, '0081', 'Professional Fees (Depreciation)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (170, '1001', 'Stock');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (171, '1002', 'Work in Progress');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (172, '1003', 'Finished Goods');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (173, '1004', 'Raw Materials');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (174, '1100', 'Debtors Control Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (175, '1101', 'Sundry Debtors');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (176, '1102', 'Other Debtors');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (177, '1103', 'Prepayments');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (178, '1104', 'Inter-company Debtors');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (179, '1105', 'PRL Platinum Retail Limited');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (180, '1106', 'Provision for doubtful debts');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (181, '1107', 'Loan Account : Operators');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (182, '1108', 'Others debtors-Difference in DRS And PSR');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (183, '1109', 'Certas Energy - Cash Bond');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (184, '1110', 'DRS Commissions-Rhina Sutton - Loan Advance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (185, '1111', 'Penlan Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (186, '1112', 'Edmonton Service station');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (187, '1113', 'Dearnside Motor Company LTD-Intercompany');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (188, '1114', 'HKS Retail Limited');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (189, '1115', 'Site Local Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (190, '1116', 'Fuelstop-InterCompany');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (191, '1117', 'Linvick Ltd-Intercompany');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (192, '1118', 'Snakeslane roundwood station');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (193, '1119', 'M SRITHARAN SEJ');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (194, '1120', 'FORMCRAFT LIMITED SEJ');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (195, '1121', 'Swan');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (196, '1122', 'ELLAND -Inter Company');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (197, '1123', 'Rainbow Service Station-Intercompany');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (198, '1124', 'Haresfinch');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (199, '1125', 'W M KALIM SEJ');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (200, '1126', 'BENTLEY SSTN');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (201, '1127', 'Delph service station-Shop');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (202, '1128', 'Saxon Operator (Shop)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (203, '1129', 'Jamie Loan Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (204, '1130', 'Jubits Service Station - Shop(sathees)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (205, '1131', 'West End Service Station - Shop(sathees)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (206, '1132', 'V S SERVICES LOAN  SEJ');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (207, '1133', 'Autopitstop Operator');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (208, '1134', 'Crankhall Lane Service station');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (209, '1135', 'Jubits Lane-from 25.09.2019');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (210, '1136', '(Not in use)West End- From 25.09.2019');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (211, '1137', 'Jubits-New Operator(after 11.11.2019)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (212, '1138', 'West-New Operator(after  11.11.2019)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (213, '1139', 'R''oLeary(Furnival)-Intercompany');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (214, '1140', 'RYAN');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (215, '1141', 'Fuel Efficient');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (216, '1142', 'Trustees of the Motor Fuel Limited Directors Pension Scheme');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (217, '1143', 'JBROS (Investments) Ltd-Intercompany');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (218, '1144', '303 PRESTON ROAD LIMITED');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (219, '1145', 'JOHN CORBO');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (220, '1146', 'SLOANPLUMB WOOD');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (221, '1147', 'LOAN-Dummy Code');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (222, '1148', 'White Rose Service Station-Intercompany');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (223, '1149', 'NEXA-matthew');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (224, '1150', 'NEXA-MFG-10351');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (225, '1151', 'NEXA- MI/12239-New facilities with Lloyds Bank plc');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (226, '1152', 'NEXA-CLOSED');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (227, '1153', 'NEXA-Matter: MI/8186');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (228, '1154', 'NEXA-8187(Loans to Easy Property Group Limited and The Easy');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (229, '1155', 'NEXA-8651(Miscellaneous matters)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (230, '1156', 'NOT IN USE');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (231, '1157', 'NEXA-MI/14080-(90 Sedgley Limited (Kings Garage)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (232, '1158', 'NEXA-MI/12344-Artorius: Station Rd, Gnosall and Minsterley,');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (233, '1159', 'NEXA-MI/8635-(Springbank Garage, Nelson: acquisition)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (234, '1160', 'NEXA-MI/15327-Esso PFS and former Volvo, Reckleford, Yeovil');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (235, '1161', 'NEXA-MI/16854-Kegworth Service Station');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (236, '1162', 'NEXA-MI/16857-Canklow Service Station');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (237, '1163', 'NEXA-MI/18621-Harvest (Doncaster), Portway (Milton),West');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (238, '1164', 'NEXA-MI/23186-Vale Service Station, Ashton under Hill, Evesh');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (239, '1165', 'NEXA-MI/22587-guyhirn - lease of old cafe part of site');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (240, '1166', 'NEXA-MI/8053');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (241, '1167', 'NEXA-Matter: MI/8181');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (242, '1168', 'NEXA-MI/27187-Stanton Service Station');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (243, '1169', 'NEXA-MI/24324');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (244, '1170', 'NEXA-MI/27925');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (245, '1198', 'Unidentified Payment');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (246, '1200', 'PRL (HSBC A/C 02739186)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (247, '1205', 'Penlan (HSBC A/C 42802937)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (248, '1210', 'Lanner Moor (HSBC A/C 42802929)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (249, '1215', 'Edmonton Service ( HSBC A/C 84370023)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (250, '1220', 'Luton Connect (HSBC 04435427)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (251, '1223', 'EDMONTON A/C  50110515');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (252, '1224', 'Lloyds Bank( 34969060)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (253, '1225', 'PRL (HSBC A/C 02739194)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (254, '1226', 'Hen & Chicken - HSBC A/c 74400046');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (255, '1230', 'Petty Cash');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (256, '1231', 'Manor A/C 80110485');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (257, '1232', 'Float Money');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (258, '1234', 'Luton (HSBC A/C 50110523)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (259, '1235', 'Hen & Chicken ( HSBC A/c  50110507');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (260, '1236', 'Commercial Mortgage ( HSBC A/c 90458031)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (261, '1237', 'Other Deposits');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (262, '1240', 'Company Credit Card');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (263, '1245', 'Shell Kempston ( A/c 24542517)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (264, '1246', 'Shell Kempston ( A/C 80110477)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (265, '1249', 'DEPOSITS (Refundable)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (266, '1250', 'Manor Connect (HSBC A/C 04435435)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (267, '1255', 'Kings Lane ( HSBC A/c 83832090 )');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (268, '1260', 'Shell St. Christopher ( A/c 04542495)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (269, '1261', 'Christopher A/C 80110493');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (270, '1265', 'KLSS Bank Loan ( HSBC  A/c 80042803 )');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (271, '1266', 'Mortgage (Hsbc A/c-91107496)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (272, '1270', 'Dearnside Motor');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (273, '1275', 'Kegworth(HSBC A/C 43839052)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (274, '1276', 'Lloyds Loan A');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (275, '1277', 'Lloyds Loan B');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (276, '1278', 'PRL Lloyd Loan A/c:L2002600323');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (277, '1279', 'MFG -HSBC Loan (Facility B)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (278, '1280', 'Lloyds -Jubit Lane(35223068)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (279, '1281', 'Lloyds  Worsley Brow(35217068)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (280, '1282', 'Lloyds -West End Road(35454360)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (281, '1283', 'Lloyds  Haresfinch(35222668)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (282, '1284', 'Lloyds - PRL A/c 34969060');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (283, '1285', 'LLoyds : PRL (A/c 145643 Dearnside )');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (284, '1286', 'DUMMY BANK');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (285, '1287', 'PRL(00357748)-Lloyds bank');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (286, '1288', 'Loan SAL A/c-00546941');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (287, '1289', 'Haresfich (A/C No.38807660)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (288, '1290', 'PRL Lloyds Loan A/c:01630413');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (289, '1291', 'PRL Lloyds Loan A/c:01635113');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (290, '1292', 'Loan A/c :40116071218719(HSBC)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (291, '1293', 'Lloyds Bank-Dearnside A/c-35280668');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (292, '1294', 'HSBC Loan A/C-54040368');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (293, '1295', 'HSBC Loan (Facility A)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (294, '1296', 'new loan-matthew');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (295, '1297', 'BP Loan');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (296, '1298', 'PRL Lloyd Loan A/c:L2002561514');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (297, '1299', 'PRL Lloyd Loan A/c:L2002600323');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (298, '1300', 'Cash');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (299, '1301', 'VISA SWITCH');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (300, '1302', 'BP');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (301, '1303', 'Shell');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (302, '1304', 'Allstar');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (303, '1305', 'Amex');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (304, '1306', 'Texaco');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (305, '1307', 'OTHERS');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (306, '1308', 'Local Accounts');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (307, '2100', 'Creditors Control Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (308, '2101', 'Sundry Creditors');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (309, '2102', 'Other Creditors');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (310, '2103', 'Blake Morgan');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (311, '2104', 'Nexa-Loan Closer');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (312, '2105', 'Dearnsdie Motor Co.');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (313, '2106', 'MI-10777-Ptarmigan Holdings Ltd');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (314, '2107', 'BP Dealer Loan');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (315, '2108', 'Unidentified Receipt');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (316, '2109', 'Accruals');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (317, '2200', 'Sales Tax Control Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (318, '2201', 'Purchase Tax Control Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (319, '2202', 'VAT Liability');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (320, '2204', 'Manual Adjustments');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (321, '2205', 'Union OSS Tax Control Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (322, '2206', 'Non-union OSS Tax Control Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (323, '2207', 'IOSS Tax Control Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (324, '2210', 'P.A.Y.E.');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (325, '2211', 'National Insurance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (326, '2220', 'Net Wages');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (327, '2230', 'Pension Fund');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (328, '2300', 'Loans realted to directors');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (329, '2301', 'Directors Loan Accounts (Director 1)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (330, '2302', 'Directors Loan Accounts (Director 2)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (331, '2303', 'Directors Loan Account (Linda)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (332, '2310', 'Opening Trial Balance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (333, '2320', 'Corporation Tax');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (334, '2321', 'Deferred tax liability');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (335, '2330', 'Mortgages');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (336, '3000', 'Ordinary Shares');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (337, '3001', 'Share Premium');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (338, '3010', 'Preference Shares');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (339, '3100', 'Revaluation Reserves');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (340, '3101', 'Undistributed Reserves');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (341, '3200', 'Profit and Loss Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (342, '4000', 'Petrol-Sales');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (343, '4001', 'Diesel-Sales');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (344, '4002', 'Super Petrol-Sales');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (345, '4003', 'Super Diesel-Sales');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (346, '4004', 'Sales : Edmonton Service Sation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (347, '4005', 'Sales : Penlan Service Station');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (348, '4006', 'Sales - Shop Floor');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (349, '4007', 'Sales : Car Wash');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (350, '4008', 'AdBlue-Sales');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (351, '4009', 'Discounts Allowed');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (352, '4010', 'National Lottery');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (353, '4011', 'Paypoint');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (354, '4012', 'Texaco - UK Fuels');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (355, '4013', 'Costa Sales');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (356, '4014', 'LPG-Sales');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (357, '4099', 'unused');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (358, '4100', 'Penlan Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (359, '4101', 'Edmonton Service Station Account');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (360, '4200', 'Sales of Assets');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (361, '4400', 'Bunkering Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (362, '4900', 'Operating Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (363, '4901', 'ATM Machine Income');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (364, '4902', 'Commissions Received');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (365, '4903', 'Insurance Claims');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (366, '4904', 'Rent Income');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (367, '4905', 'Daily Facility Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (368, '4906', 'Bank Deposit Interest Received');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (369, '4907', 'Sundry Income');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (370, '4908', 'Other Interest received');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (371, '5000', 'Petrol-Purchases');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (372, '5001', 'Diesel-Purchases');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (373, '5002', 'Miscellaneous Purchases');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (374, '5003', 'Super Petrol-Purchases');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (375, '5004', 'Super Diesel-Purchases');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (376, '5005', 'Purchases : Shop Floor');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (377, '5006', 'National Lottery');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (378, '5007', 'Car Wash Material-Purchases');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (379, '5008', 'Stock from Operators-Purchases');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (380, '5009', 'Service Pumps');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (381, '5010', 'Costa Purchase');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (382, '5011', 'Liquid Petrolium Gas');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (383, '5012', 'EPAY/PAYPOINT');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (384, '5013', 'Margin Share');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (385, '5014', 'AdBlue-Purchases');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (386, '5015', 'LPG-Purcahase');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (387, '5100', 'Health & Safety - Audit and Risk Assessment');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (388, '5101', 'Polling Fee (not to use)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (389, '5102', 'Other Purchases-(Fuel Promotional)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (390, '5103', 'Agency Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (391, '5104', 'Fuel Promotional');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (392, '5105', 'Credit Card Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (393, '5200', 'Stock Movement');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (394, '5201', 'Closing Stock');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (395, '5202', 'Purchase of Stock - 4 Sites in St Helens');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (396, '6000', 'Productive Labour');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (397, '6001', 'Cost of Sales Labour');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (398, '6002', 'Sub-Contractors');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (399, '6100', 'Fuel Commissions');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (400, '6101', 'Daily Facility Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (401, '6102', 'Valeting Facility Commissions');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (402, '6200', 'Sales Promotions');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (403, '6201', 'Marketing & Advertising');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (404, '6202', 'Gifts and Samples');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (405, '6203', 'P.R. (Literature & Brochures)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (406, '6204', 'Site Operator Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (407, '6205', 'Vouchers');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (408, '6900', 'Miscellaneous Expenses');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (409, '7000', 'Gross Wages');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (410, '7001', 'Bonus');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (411, '7002', 'Directors Remuneration');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (412, '7003', 'Staff Salaries - Luton');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (413, '7004', 'Wages - Regular');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (414, '7005', 'Wages - Casual');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (415, '7006', 'Employers N.I. (Non-Directors)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (416, '7007', 'Staff Pensions Costs');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (417, '7008', 'Recruitment Expenses');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (418, '7009', 'Adjustments');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (419, '7010', 'SSP Reclaimed');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (420, '7011', 'SMP Reclaimed');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (421, '7012', 'Employers N.I. (Directors)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (422, '7099', 'Marketing & Advertisement');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (423, '7100', 'Rent');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (424, '7102', 'Water Rates');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (425, '7103', 'General Rates');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (426, '7104', 'Premises Insurance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (427, '7200', 'Electricity');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (428, '7201', 'Gas');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (429, '7202', 'Oil');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (430, '7203', 'Other Heating Costs');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (431, '7300', 'Vehicle Fuel');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (432, '7301', 'Vehicle Repairs and Servicing');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (433, '7302', 'Vehicle Hire');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (434, '7303', 'Vehicle Insurance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (435, '7304', 'Motor Vehicle Rental Expenses');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (436, '7305', 'Congestion Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (437, '7306', 'Mileage Claims+Insurance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (438, '7350', 'Scale Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (439, '7400', 'Travelling');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (440, '7401', 'Car Hire');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (441, '7402', 'Hotels');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (442, '7403', 'U.K. Entertainment');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (443, '7404', 'Overseas Entertainment');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (444, '7405', 'Overseas Travelling');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (445, '7406', 'Subsistence');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (446, '7500', 'Printing');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (447, '7501', 'Postage and Carriage');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (448, '7502', 'Office Stationery');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (449, '7503', 'Computer Expenses');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (450, '7505', 'Freight Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (451, '7550', 'Telephone and Fax');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (452, '7551', 'Internet Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (453, '7552', 'Computers & Software');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (454, '7553', 'Mobile Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (455, '7600', 'Legal Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (456, '7601', 'Audit Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (457, '7602', 'Accountancy Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (458, '7603', 'Consultancy Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (459, '7604', 'Professional Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (460, '7605', 'Management Charges Payable');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (461, '7606', 'Software Subscriptions');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (462, '7607', 'Royalty Fee');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (463, '7700', 'Equipment Hire');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (464, '7701', 'Office Machine Maintenance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (465, '7702', 'Equipment Leasing, Repair and Hire');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (466, '7703', 'Leasing');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (467, '7752', 'Arrangement Fees');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (468, '7800', 'Burglar Alarm - Security/Fire protection');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (469, '7801', 'Repairs and Renewals');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (470, '7802', 'Cleaning Expenses');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (471, '7803', 'Premises Expenses');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (472, '7804', 'Penalty Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (473, '7900', 'Bank Interest Paid');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (474, '7901', 'Bank Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (475, '7902', 'Currency Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (476, '7903', 'Loan Interest Paid');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (477, '7904', 'H.P. Interest');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (478, '7905', 'Credit Charges (inc Polling)');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (479, '7906', 'Exchange Rate Variance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (480, '7907', 'Other Interest Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (481, '7908', 'Factoring Charges');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (482, '7909', 'Black Morgan');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (483, '7980', 'Delph & Saxon Prelim W/O');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (484, '8000', 'Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (485, '8001', 'Plant/Machinery Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (486, '8002', 'Furniture/Fitting Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (487, '8003', 'Vehicle Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (488, '8004', 'Office Equipment Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (489, '8005', 'Others Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (490, '8006', 'Property Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (491, '8007', 'Intangible Assets Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (492, '8008', 'Improvement of Assets- Depreciation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (493, '8009', 'Professional Fees-Amortisation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (494, '8100', 'Bad Debt Write Off');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (495, '8102', 'Bad Debt Provision');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (496, '8200', 'Donations');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (497, '8201', 'Subscriptions & Licences');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (498, '8202', 'Clothing Costs');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (499, '8203', 'Training Costs');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (500, '8204', 'Insurance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (501, '8205', 'Refreshments');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (502, '8206', 'Cash Register Discrepancies');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (503, '8207', 'Site Consumables');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (504, '8208', 'Staff Expenses');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (505, '8209', 'BPME');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (506, '8245', 'Premises Insurance');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (507, '8250', 'Sundry Expenses');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (508, '8251', 'P/L on Sale/Disposal of Asst');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (509, '9000', 'Deferred tax');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (510, '9001', 'Taxation');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (511, '9996', 'Daily Cash POsting Suspense');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (512, '9997', 'Daily Cash Posting control');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (513, '9998', 'misposting supplier');
INSERT INTO public.nominal_code (id, code, object_name) VALUES (514, '9999', 'Mispostings Customer');


--
-- Data for Name: site_mappings; Type: TABLE DATA; Schema: public; Owner: bill_user
--

INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (1, 'Manor Service Station', '6', 'Man', 'PRL', 'IP31 2BZ', 'MANBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (2, 'Hen & Chicken Service Station', '7', 'Hen', 'PRL', 'IP31 2BZ', 'HENBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (3, 'Salterton Road Service Station', '9', 'Sal', 'PRL', 'IP31 2BZ', 'SALBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (4, 'Lanner Moor Garage', '10', 'Lan', 'PRL', 'IP31 2BZ', 'LANBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (5, 'Luton Road Service Station', '11', 'Lut', 'PRL', 'IP31 2BZ', 'LUTBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (6, 'Kings Lane Service Station', '14', 'Kin', 'PRL', 'IP31 2BZ', 'KINBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (7, 'Delph Service Station', '17', 'Del', 'PRL', 'IP31 2BZ', 'DELBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (8, 'Saxon Autopoint Ss', '18', 'Sax', 'PRL', 'IP31 2BZ', 'SAXBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (9, 'Jubits Lane Sstn', '19', 'Jub', 'PRL', 'IP31 2BZ', 'JUBBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (10, 'Worsley Brow', '20', 'Wor', 'PRL', 'IP31 2BZ', 'WORBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (11, 'Auto Pitstop', '23', 'Auto', 'PRL', 'IP31 2BZ', 'AUTBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (12, 'Crown Service Station', '24', 'Cro', 'PRL', 'IP31 2BZ', 'CROWBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (13, 'Marsland Service Station', '25', 'Mar', 'PRL', 'IP31 2BZ', 'MARBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (14, 'Gemini Service Station', '29', 'Gem', 'PRL', 'IP31 2BZ', 'GEMBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (15, 'Park View', '30', 'Park', 'PRL', 'IP31 2BZ', 'PARBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (16, 'Filleybrook S Stn', '31', 'Fil', 'PRL', 'IP31 2BZ', 'FILBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (17, 'Swan Connect', '33', 'Swan', 'PRL', 'IP31 2BZ', 'SWABPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (18, 'Portland', '34', 'Port', 'PRL', 'IP31 2BZ', 'PORBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (19, 'Lower Lane', '35', 'Low', 'PRL', 'IP31 2BZ', 'LOWBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (20, 'Vale Service Station', '36', 'Vale', 'PRL', 'IP31 2BZ', 'VALBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (21, 'Kensington Service Station', '37', 'Ken', 'PRL', 'IP31 2BZ', 'KENBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (22, 'County Oak Service Station', '38', 'Cou', 'PRL', 'IP31 2BZ', 'COUBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (23, 'Kings Of Sedgley', '39', 'King', 'PRL', 'IP31 2BZ', 'SEDBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (24, 'Gnosall Service Station', '40', 'Gno', 'PRL', 'IP31 2BZ', 'GNOBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (25, 'Minsterley Service Station', '41', 'Min', 'PRL', 'IP31 2BZ', 'MINBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (26, 'Nelson Service Station', '42', 'Nel', 'PRL', 'IP31 2BZ', 'NELBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (27, 'Yeovil Service Station', '43', 'Yeo', 'PRL', 'IP31 2BZ', 'YEOBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (28, 'Canklow Service Station', '44', 'Can', 'PRL', 'IP31 2BZ', 'CANBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (29, 'Stanton Self Serve', '45', 'Sta', 'PRL', 'IP31 2BZ', 'STABPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (30, 'West End Service Station', '1', 'West HW', 'Linwick', 'HP12 3AB', 'WEHBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (31, 'Dove Retail Ltd', '1', NULL, 'White Rose', 'S75 1JU', 'DOVBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (32, 'Deamside Motor Company Ltd', '1', 'Deamside', 'Deamside', 'S63 9AE', 'DEABPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (33, 'Ansty Cross Garage', '2', 'Ansty', 'Deamside', 'RH17 5AG', 'ANSBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (34, 'Market Street Service Station', '1', 'Mar', 'Jbros', 'OL13 0AZ', 'MARBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (35, 'Ramper Service Station', '2', 'Ram', 'Jbros', 'LN6 9NP', 'RAMBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (36, 'Pennine Service Station', '3', 'Pen', 'Jbros', 'HD2 1QD', 'PENBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (37, 'Elstow Road Service Station', '4', 'Elstow', 'Jbros', 'MK42 9NU', 'ELSBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (38, 'Portway Service Station', '5', 'Portway', 'Jbros', 'MK13 8HR', 'PORBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (39, 'Downs Service Station', '6', 'Down', 'Jbros', 'LU6 2PX', 'DOWBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (40, 'Woodside Garage', '7', 'Woodside', 'Jbros', 'NP15 1SS', 'WOOBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (41, 'Farley Green Filling Station', '8', 'Farley', 'Jbros', 'LU1 5QA', 'FARBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (42, 'Monkshill Service Station', '10', 'Monk', 'Jbros', 'S63 9AP', 'MONBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (43, 'Lockwood Filling Station', '11', 'Lockwood', 'Jbros', 'HD4 6EP', 'LOCBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (44, 'Burton Service Station', '12', 'Burton', 'Jbros', 'DE15 0NX', 'BURBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (45, 'Wittering Service Station', '13', 'Wittering', 'Jbros', 'PE8 6HA', 'WITBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (46, 'Bloody Oaks Service Station', '14', 'Bloody Oak', 'Jbros', 'PE9 4AD', 'BLOBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (47, 'Prizet South Service Station', '15', 'Prizet', 'Jbros', 'LA8 8AA', 'PRIBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (48, 'Souldrop Service Station', '16', 'Soul', 'Jbros', 'MK44 1HJ', 'SOUBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (49, 'Storrington Service Station', '17', 'Stor', 'Jbros', 'RH20 4NF', 'STOBPOIL');
INSERT INTO public.site_mappings (id, site_name, dept, short_code, company, post_code, ac_code) VALUES (50, 'Hawkswood Service Station', '18', 'Hawkswood', 'Jbros', 'BN27 1UG', 'HAWBPOIL');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: bill_user
--

INSERT INTO public.users (id, email, password_hash, role, accessible_companies, is_active, created_at, created_by) VALUES (1, 'ayush23854@gmail.com', '24c66a7752f59827d06059ca515b2f95c2ec7c22212c357316d4e8c724418c34', 'admin', NULL, true, NULL, 'system');
INSERT INTO public.users (id, email, password_hash, role, accessible_companies, is_active, created_at, created_by) VALUES (7, 'ayushraj613718@gmail.com', '30ebfe234a9939a6fc1dc46ac0d64114ec9cf5f153f3fe8038346318dde52d83', 'user', '["PRL"]', true, NULL, 'ayush23854@gmail.com');


--
-- Name: company_email_mapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bill_user
--

SELECT pg_catalog.setval('public.company_email_mapping_id_seq', 2, true);


--
-- Name: nominal_code_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bill_user
--

SELECT pg_catalog.setval('public.nominal_code_id_seq', 514, true);


--
-- Name: site_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bill_user
--

SELECT pg_catalog.setval('public.site_mappings_id_seq', 50, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: bill_user
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- PostgreSQL database dump complete
--

\unrestrict 8oHFQR1A9pYwhzD79YQBEad58lWHt4XLluLhucGsHg6V8GN49K7LkUzy9jjR9VO

