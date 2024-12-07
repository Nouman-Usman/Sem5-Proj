USE [master]
GO
/****** Object:  Database [Apna_Waqeel]    Script Date: 12/7/2024 1:15:29 PM ******/
CREATE DATABASE [Apna_Waqeel]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'Apna_Waqeel', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.NOUMAN\MSSQL\DATA\Apna_Waqeel.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'Apna_Waqeel_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.NOUMAN\MSSQL\DATA\Apna_Waqeel_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO
ALTER DATABASE [Apna_Waqeel] SET COMPATIBILITY_LEVEL = 160
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [Apna_Waqeel].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [Apna_Waqeel] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET ARITHABORT OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [Apna_Waqeel] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [Apna_Waqeel] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET  DISABLE_BROKER 
GO
ALTER DATABASE [Apna_Waqeel] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [Apna_Waqeel] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET RECOVERY FULL 
GO
ALTER DATABASE [Apna_Waqeel] SET  MULTI_USER 
GO
ALTER DATABASE [Apna_Waqeel] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [Apna_Waqeel] SET DB_CHAINING OFF 
GO
ALTER DATABASE [Apna_Waqeel] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [Apna_Waqeel] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [Apna_Waqeel] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [Apna_Waqeel] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
EXEC sys.sp_db_vardecimal_storage_format N'Apna_Waqeel', N'ON'
GO
ALTER DATABASE [Apna_Waqeel] SET QUERY_STORE = ON
GO
ALTER DATABASE [Apna_Waqeel] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
USE [Apna_Waqeel]
GO
/****** Object:  Table [dbo].[Users]    Script Date: 12/7/2024 1:15:30 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Users](
    [UserId] [uniqueidentifier] PRIMARY KEY DEFAULT NEWID(),
    [UserName] [nvarchar](255) NOT NULL,
    [Email] [nvarchar](255) UNIQUE NOT NULL,
    [CreatedAt] [datetime2](7) DEFAULT GETDATE(),
    [UserType] [nvarchar](50) NOT NULL CHECK (UserType IN ('Customer', 'Lawyer', 'Admin'))
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ChatTopics]    Script Date: 12/7/2024 1:15:30 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ChatTopics](
	[TopicId] [uniqueidentifier] NOT NULL,
	[UserId] [nvarchar](255) NOT NULL,
	[Topic] [nvarchar](max) NOT NULL,
	[Timestamp] [datetime2](7) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[TopicId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Customers]    Script Date: 12/7/2024 1:15:30 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Customers](
	[CustomerId] [nvarchar](255) NOT NULL,
	[CustomerName] [nvarchar](255) NOT NULL,
	[ContactInfo] [nvarchar](max) NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[CustomerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Lawyers]    Script Date: 12/7/2024 1:15:30 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
DROP TABLE IF EXISTS [dbo].[Lawyers]
CREATE TABLE [dbo].[Lawyers](
    [LawyerId] [int] IDENTITY(1,1) PRIMARY KEY,
    [LawyerName] [nvarchar](255) NOT NULL,
    [ContactInfo] [nvarchar](max) NOT NULL,
    [CreatedAt] [datetime2](7) NOT NULL
)
GO
/****** Object:  Table [dbo].[LawyerStore]    Script Date: 12/7/2024 1:15:30 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
DROP TABLE IF EXISTS [dbo].[LawyerStore]
CREATE TABLE [dbo].[LawyerStore](
    [LawyerId] [int] NOT NULL,
    [LawyerName] [varchar](50) NOT NULL,
    [Email] [varchar](50) NOT NULL,
    [CreatedAt] [date] NOT NULL,
    [Specialization] [varchar](50) NOT NULL,
    [Experience] [varchar](50) NOT NULL,
    [Rating] [varchar](50) NOT NULL,
    [Location] [varchar](50) NOT NULL,
    [Contact] [varchar](50) NOT NULL,
    CONSTRAINT [FK_LawyerStore_Lawyers] FOREIGN KEY ([LawyerId]) 
        REFERENCES [dbo].[Lawyers] ([LawyerId])
)
GO
CREATE INDEX [IX_LawyerStore_LawyerId] ON [dbo].[LawyerStore]([LawyerId])
GO
/****** Object:  Table [dbo].[Metadata]    Script Date: 12/7/2024 1:15:30 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Metadata](
	[Id] [uniqueidentifier] NOT NULL,
	[UserId] [nvarchar](255) NOT NULL,
	[ChatId] [nvarchar](255) NOT NULL,
	[Metadata] [nvarchar](max) NOT NULL,
	[Timestamp] [datetime2](7) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Sessions]    Script Date: 12/7/2024 1:15:30 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Sessions](
	[SessionId] [uniqueidentifier] NOT NULL,
	[UserId] [nvarchar](255) NOT NULL,
	[ChatId] [nvarchar](255) NOT NULL,
	[StartTime] [datetime2](7) NOT NULL,
	[EndTime] [datetime2](7) NULL,
	[SessionData] [nvarchar](max) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[SessionId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
CREATE TABLE [dbo].[UserProfiles] (
    [ProfileId] [uniqueidentifier] PRIMARY KEY DEFAULT NEWID(),
    [UserId] [uniqueidentifier] NOT NULL,
    [ContactNumber] [nvarchar](20),
    [Address] [nvarchar](500),
    [LastUpdated] [datetime2](7) DEFAULT GETDATE(),
    CONSTRAINT [FK_UserProfiles_Users] FOREIGN KEY ([UserId]) 
        REFERENCES [dbo].[Users] ([UserId]) ON DELETE CASCADE
) ON [PRIMARY]
GO
CREATE TABLE [dbo].[LawyerDetails] (
    [LawyerId] [uniqueidentifier] PRIMARY KEY,
    [Specialization] [nvarchar](100) NOT NULL,
    [Experience] [int] NOT NULL,
    [LicenseNumber] [nvarchar](50) UNIQUE NOT NULL,
    [Rating] [decimal](3,2) CHECK (Rating >= 0 AND Rating <= 5),
    [Location] [nvarchar](255) NOT NULL,
    CONSTRAINT [FK_LawyerDetails_Users] FOREIGN KEY ([LawyerId])
        REFERENCES [dbo].[Users] ([UserId])
) ON [PRIMARY]
GO
CREATE TABLE [dbo].[LawyerSpecializations] (
    [SpecializationId] [uniqueidentifier] PRIMARY KEY DEFAULT NEWID(),
    [Name] [nvarchar](100) UNIQUE NOT NULL
) ON [PRIMARY]
GO
CREATE TABLE [dbo].[LawyerSpecializationMapping] (
    [LawyerId] [uniqueidentifier],
    [SpecializationId] [uniqueidentifier],
    PRIMARY KEY ([LawyerId], [SpecializationId]),
    CONSTRAINT [FK_SpecMapping_Lawyer] FOREIGN KEY ([LawyerId])
        REFERENCES [dbo].[LawyerDetails] ([LawyerId]),
    CONSTRAINT [FK_SpecMapping_Specialization] FOREIGN KEY ([SpecializationId])
        REFERENCES [dbo].[LawyerSpecializations] ([SpecializationId])
) ON [PRIMARY]
GO
CREATE TABLE [dbo].[ChatSessions] (
    [ChatId] [uniqueidentifier] PRIMARY KEY DEFAULT NEWID(),
    [InitiatorId] [uniqueidentifier] NOT NULL,
    [RecipientId] [uniqueidentifier] NOT NULL,
    [StartTime] [datetime2](7) DEFAULT GETDATE(),
    [EndTime] [datetime2](7),
    [Status] [nvarchar](20) CHECK (Status IN ('Active', 'Closed', 'Archived')),
    CONSTRAINT [FK_ChatSessions_Initiator] FOREIGN KEY ([InitiatorId])
        REFERENCES [dbo].[Users] ([UserId]),
    CONSTRAINT [FK_ChatSessions_Recipient] FOREIGN KEY ([RecipientId])
        REFERENCES [dbo].[Users] ([UserId])
) ON [PRIMARY]
GO
CREATE TABLE [dbo].[ChatMessages](
    [MessageId] [uniqueidentifier] PRIMARY KEY DEFAULT NEWID(),
    [ChatId] [uniqueidentifier] NOT NULL,
    [SenderId] [uniqueidentifier] NOT NULL,
    [Message] [nvarchar](max) NOT NULL,
    [MessageType] [nvarchar](50) NOT NULL,
    [Timestamp] [datetime2](7) DEFAULT GETDATE(),
    CONSTRAINT [FK_ChatMessages_Chat] FOREIGN KEY ([ChatId])
        REFERENCES [dbo].[ChatSessions] ([ChatId]),
    CONSTRAINT [FK_ChatMessages_Sender] FOREIGN KEY ([SenderId])
        REFERENCES [dbo].[Users] ([UserId])
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[UserSessions]    Script Date: 12/7/2024 1:15:30 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[UserSessions](
	[SessionId] [uniqueidentifier] NOT NULL,
	[UserId] [nvarchar](255) NOT NULL,
	[StartTime] [datetime2](7) NOT NULL,
	[EndTime] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[SessionId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_ChatMessages_UserId_ChatId]    Script Date: 12/7/2024 1:15:30 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatMessages_UserId_ChatId] ON [dbo].[ChatMessages]
(
	[SenderId] ASC,
	[ChatId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
CREATE INDEX [IX_UserProfiles_UserId] ON [dbo].[UserProfiles]([UserId]);
GO
CREATE INDEX [IX_ChatMessages_ChatId] ON [dbo].[ChatMessages]([ChatId]);
GO
CREATE INDEX [IX_ChatSessions_Users] ON [dbo].[ChatSessions]([InitiatorId], [RecipientId]);
GO
CREATE INDEX [IX_LawyerDetails_Specialization] ON [dbo].[LawyerDetails]([Specialization]);
GO
USE [master]
GO
ALTER DATABASE [Apna_Waqeel] SET  READ_WRITE 
GO
