-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 06, 2025 at 10:33 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `prism_ai_database`
--

-- --------------------------------------------------------

--
-- Table structure for table `business`
--

CREATE TABLE `business` (
  `businessId` int(11) NOT NULL,
  `name` varchar(40) DEFAULT NULL,
  `contact` varchar(40) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `template` varchar(200) DEFAULT NULL,
  `prompt` varchar(200) DEFAULT NULL,
  `agentStatus` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `business`
--

INSERT INTO `business` (`businessId`, `name`, `contact`, `password`, `type`, `template`, `prompt`, `agentStatus`) VALUES
(1, 'test', '0728000031', 'test', 'test', 'test', 'test', 0);

-- --------------------------------------------------------

--
-- Table structure for table `chatlog`
--

CREATE TABLE `chatlog` (
  `msgId` int(11) NOT NULL,
  `customerId` int(11) DEFAULT NULL,
  `businessId` int(11) DEFAULT NULL,
  `productId` int(11) DEFAULT NULL,
  `LLM_msg` varchar(100) DEFAULT NULL,
  `customer_msg` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `chatlog`
--

INSERT INTO `chatlog` (`msgId`, `customerId`, `businessId`, `productId`, `LLM_msg`, `customer_msg`) VALUES
(2, 4, 1, 1, 'test', 'test');

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `customerId` int(11) NOT NULL,
  `mobileNo` varchar(20) DEFAULT NULL,
  `fName` varchar(30) DEFAULT NULL,
  `pastConversation` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`customerId`, `mobileNo`, `fName`, `pastConversation`) VALUES
(4, '0728000031', 'test', 1);

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `productId` int(11) NOT NULL,
  `businessId` int(11) NOT NULL,
  `name` varchar(40) DEFAULT NULL,
  `price` varchar(30) DEFAULT NULL,
  `description` varchar(60) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`productId`, `businessId`, `name`, `price`, `description`) VALUES
(1, 1, 'test', '100', 'test');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `business`
--
ALTER TABLE `business`
  ADD PRIMARY KEY (`businessId`);

--
-- Indexes for table `chatlog`
--
ALTER TABLE `chatlog`
  ADD PRIMARY KEY (`msgId`),
  ADD KEY `customerId` (`customerId`),
  ADD KEY `businessId` (`businessId`),
  ADD KEY `productId` (`productId`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`customerId`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`productId`),
  ADD KEY `businessId` (`businessId`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `business`
--
ALTER TABLE `business`
  MODIFY `businessId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `chatlog`
--
ALTER TABLE `chatlog`
  MODIFY `msgId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `customerId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `chatlog`
--
ALTER TABLE `chatlog`
  ADD CONSTRAINT `chatlog_ibfk_1` FOREIGN KEY (`customerId`) REFERENCES `customer` (`customerId`),
  ADD CONSTRAINT `chatlog_ibfk_2` FOREIGN KEY (`businessId`) REFERENCES `business` (`businessId`),
  ADD CONSTRAINT `chatlog_ibfk_3` FOREIGN KEY (`productId`) REFERENCES `product` (`productId`);

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`businessId`) REFERENCES `business` (`businessId`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
