-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 08, 2025 at 10:10 AM
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
  `prompt` varchar(200) DEFAULT NULL,
  `parameters` varchar(100) DEFAULT NULL,
  `agentStatus` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `business`
--

INSERT INTO `business` (`businessId`, `name`, `contact`, `password`, `type`, `prompt`, `parameters`, `agentStatus`) VALUES
(1, 'Alice', '+1234567890', 'secureP@ss123', 'admin', 'Generate a product description for a new smart home device.', '{\'tone\': \'professional\', \'length\': \'short\', \'language\': \'English\'}', 0),
(2, 'Alice', '+1234567890', 'secureP@ss123', 'admin', 'Generate a product description for a new smart home device.', '{\'tone\': \'professional\', \'length\': \'short\', \'language\': \'English\'}', 0),
(3, 'Alice', '+1234567890', 'secureP@ss123', 'admin', 'Generate a product description for a new smart home device.', '{\'tone\': \'professional\', \'length\': \'short\', \'language\': \'English\'}', 0);

-- --------------------------------------------------------

--
-- Table structure for table `campaign`
--

CREATE TABLE `campaign` (
  `campaignId` int(11) NOT NULL,
  `businessId` int(11) NOT NULL,
  `name` varchar(40) DEFAULT NULL,
  `template` varchar(200) DEFAULT NULL,
  `targetProblem` varchar(100) DEFAULT NULL,
  `targetAudience` varchar(50) DEFAULT NULL,
  `uniqueSolution` varchar(100) DEFAULT NULL,
  `whyNeeded` varchar(100) DEFAULT NULL,
  `mainBenefits` varchar(100) DEFAULT NULL,
  `socialProof` varchar(100) DEFAULT NULL,
  `price` varchar(30) DEFAULT NULL,
  `offer` varchar(100) DEFAULT NULL,
  `urgency` varchar(50) DEFAULT NULL,
  `cta` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `campaign`
--

INSERT INTO `campaign` (`campaignId`, `businessId`, `name`, `template`, `targetProblem`, `targetAudience`, `uniqueSolution`, `whyNeeded`, `mainBenefits`, `socialProof`, `price`, `offer`, `urgency`, `cta`) VALUES
(1, 3, 'GreenSprout Plant Kit', 'Gardening Product Landing Page', 'Difficulty in growing plants at home', 'Urban gardeners, plant enthusiasts, and eco-friend', 'Complete, easy-to-use plant growth kit with organic seeds and self-watering pots', 'To make home gardening simple and enjoyable', 'Low maintenance, space-saving, and eco-friendly', 'Loved by over 10,000 happy plant parents', '49.99', 'Free shipping for orders over $50', 'Limited edition kits available', 'Get Yours Now');

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
(8, '+1234567890', 'Alice', 0),
(9, '+1987654321', 'Bob', 0),
(10, '+1443234567', 'Charlie', 0),
(11, '0714711537', 'David', 0),
(12, '+1555123456', 'Eve', 0),
(13, '0728000031', 'Frank', 0);

-- --------------------------------------------------------

--
-- Table structure for table `customer_business`
--

CREATE TABLE `customer_business` (
  `customerId` int(20) DEFAULT NULL,
  `businessId` int(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customer_business`
--

INSERT INTO `customer_business` (`customerId`, `businessId`) VALUES
(8, 2),
(9, 2),
(10, 2),
(11, 2),
(12, 2),
(13, 2);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `business`
--
ALTER TABLE `business`
  ADD PRIMARY KEY (`businessId`);

--
-- Indexes for table `campaign`
--
ALTER TABLE `campaign`
  ADD PRIMARY KEY (`campaignId`),
  ADD KEY `businessId` (`businessId`);

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
-- Indexes for table `customer_business`
--
ALTER TABLE `customer_business`
  ADD KEY `customerId` (`customerId`),
  ADD KEY `businessId` (`businessId`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `business`
--
ALTER TABLE `business`
  MODIFY `businessId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `campaign`
--
ALTER TABLE `campaign`
  MODIFY `campaignId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `chatlog`
--
ALTER TABLE `chatlog`
  MODIFY `msgId` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `customer`
--
ALTER TABLE `customer`
  MODIFY `customerId` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `campaign`
--
ALTER TABLE `campaign`
  ADD CONSTRAINT `campaign_ibfk_1` FOREIGN KEY (`businessId`) REFERENCES `business` (`businessId`);

--
-- Constraints for table `chatlog`
--
ALTER TABLE `chatlog`
  ADD CONSTRAINT `chatlog_ibfk_1` FOREIGN KEY (`customerId`) REFERENCES `customer` (`customerId`),
  ADD CONSTRAINT `chatlog_ibfk_2` FOREIGN KEY (`businessId`) REFERENCES `business` (`businessId`),
  ADD CONSTRAINT `chatlog_ibfk_3` FOREIGN KEY (`productId`) REFERENCES `campaign` (`campaignId`);

--
-- Constraints for table `customer_business`
--
ALTER TABLE `customer_business`
  ADD CONSTRAINT `customer_business_ibfk_1` FOREIGN KEY (`customerId`) REFERENCES `customer` (`customerId`),
  ADD CONSTRAINT `customer_business_ibfk_2` FOREIGN KEY (`businessId`) REFERENCES `business` (`businessId`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
