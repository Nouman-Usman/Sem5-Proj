USE [master]
GO
/****** Object:  Database [Apna_Waqeel]    Script Date: 12/9/2024 9:34:23 AM ******/
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
ALTER DATABASE [Apna_Waqeel] SET  ENABLE_BROKER 
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
/****** Object:  Table [dbo].[ChatMessages]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ChatMessages](
	[MessageId] [uniqueidentifier] NOT NULL,
	[ChatId] [uniqueidentifier] NOT NULL,
	[SenderId] [uniqueidentifier] NOT NULL,
	[Message] [nvarchar](max) NOT NULL,
	[MessageType] [nvarchar](50) NOT NULL,
	[Timestamp] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[MessageId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ChatSessions]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ChatSessions](
	[ChatId] [uniqueidentifier] NOT NULL,
	[InitiatorId] [uniqueidentifier] NOT NULL,
	[RecipientId] [uniqueidentifier] NOT NULL,
	[StartTime] [datetime2](7) NULL,
	[EndTime] [datetime2](7) NULL,
	[Status] [nvarchar](20) NULL,
PRIMARY KEY CLUSTERED 
(
	[ChatId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ChatTopics]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ChatTopics](
	[TopicId] [uniqueidentifier] NOT NULL,
	[UserId] [nvarchar](255) NOT NULL,
	[Topic] [nvarchar](max) NOT NULL,
	[Timestamp] [datetime2](7) NOT NULL,
	[ChatId] [nvarchar](250) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[TopicId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Customers]    Script Date: 12/9/2024 9:34:24 AM ******/
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
/****** Object:  Table [dbo].[LawyerDetails]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[LawyerDetails](
	[LawyerId] [uniqueidentifier] NOT NULL,
	[Specialization] [nvarchar](100) NOT NULL,
	[Experience] [int] NOT NULL,
	[LicenseNumber] [nvarchar](50) NOT NULL,
	[Rating] [decimal](3, 2) NULL,
	[Location] [nvarchar](255) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[LawyerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[LicenseNumber] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Lawyers]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Lawyers](
	[LawyerId] [int] IDENTITY(1,1) NOT NULL,
	[LawyerName] [nvarchar](255) NOT NULL,
	[ContactInfo] [nvarchar](max) NOT NULL,
	[CreatedAt] [datetime2](7) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[LawyerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[LawyerSpecializationMapping]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[LawyerSpecializationMapping](
	[LawyerId] [uniqueidentifier] NOT NULL,
	[SpecializationId] [uniqueidentifier] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[LawyerId] ASC,
	[SpecializationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[LawyerSpecializations]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[LawyerSpecializations](
	[SpecializationId] [uniqueidentifier] NOT NULL,
	[Name] [nvarchar](100) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[SpecializationId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[Name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[LawyerStore]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[LawyerStore](
	[LawyerId] [int] NOT NULL,
	[LawyerName] [varchar](50) NOT NULL,
	[Email] [varchar](50) NOT NULL,
	[CreatedAt] [date] NOT NULL,
	[Specialization] [varchar](50) NOT NULL,
	[Experience] [varchar](50) NOT NULL,
	[Rating] [varchar](50) NOT NULL,
	[Location] [varchar](50) NOT NULL,
	[Contact] [varchar](50) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Metadata]    Script Date: 12/9/2024 9:34:24 AM ******/
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
/****** Object:  Table [dbo].[Sessions]    Script Date: 12/9/2024 9:34:24 AM ******/
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
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[UserProfiles]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[UserProfiles](
	[ProfileId] [uniqueidentifier] NOT NULL,
	[UserId] [uniqueidentifier] NOT NULL,
	[ContactNumber] [nvarchar](20) NULL,
	[Address] [nvarchar](500) NULL,
	[LastUpdated] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[ProfileId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Users]    Script Date: 12/9/2024 9:34:24 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Users](
	[UserId] [uniqueidentifier] NOT NULL,
	[UserName] [nvarchar](255) NOT NULL,
	[Email] [nvarchar](255) NOT NULL,
	[CreatedAt] [datetime2](7) NULL,
	[UserType] [nvarchar](50) NOT NULL,
	[PasswordHash] [nvarchar](255) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[Email] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[UserSessions]    Script Date: 12/9/2024 9:34:24 AM ******/
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
/****** Object:  Index [IX_ChatMessages_ChatId]    Script Date: 12/9/2024 9:34:24 AM ******/
CREATE NONCLUSTERED INDEX [IX_ChatMessages_ChatId] ON [dbo].[ChatMessages]
(
	[ChatId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_ChatMessages_UserId_ChatId]    Script Date: 12/9/2024 9:34:24 AM ******/
CREATE NONCLUSTERED INDEX [IX_ChatMessages_UserId_ChatId] ON [dbo].[ChatMessages]
(
	[SenderId] ASC,
	[ChatId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_ChatSessions_Users]    Script Date: 12/9/2024 9:34:24 AM ******/
CREATE NONCLUSTERED INDEX [IX_ChatSessions_Users] ON [dbo].[ChatSessions]
(
	[InitiatorId] ASC,
	[RecipientId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_LawyerDetails_Specialization]    Script Date: 12/9/2024 9:34:24 AM ******/
CREATE NONCLUSTERED INDEX [IX_LawyerDetails_Specialization] ON [dbo].[LawyerDetails]
(
	[Specialization] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_LawyerStore_LawyerId]    Script Date: 12/9/2024 9:34:24 AM ******/
CREATE NONCLUSTERED INDEX [IX_LawyerStore_LawyerId] ON [dbo].[LawyerStore]
(
	[LawyerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_UserProfiles_UserId]    Script Date: 12/9/2024 9:34:24 AM ******/
CREATE NONCLUSTERED INDEX [IX_UserProfiles_UserId] ON [dbo].[UserProfiles]
(
	[UserId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[ChatMessages] ADD  DEFAULT (newid()) FOR [MessageId]
GO
ALTER TABLE [dbo].[ChatMessages] ADD  DEFAULT (getdate()) FOR [Timestamp]
GO
ALTER TABLE [dbo].[ChatSessions] ADD  DEFAULT (newid()) FOR [ChatId]
GO
ALTER TABLE [dbo].[ChatSessions] ADD  DEFAULT (getdate()) FOR [StartTime]
GO
ALTER TABLE [dbo].[LawyerSpecializations] ADD  DEFAULT (newid()) FOR [SpecializationId]
GO
ALTER TABLE [dbo].[UserProfiles] ADD  DEFAULT (newid()) FOR [ProfileId]
GO
ALTER TABLE [dbo].[UserProfiles] ADD  DEFAULT (getdate()) FOR [LastUpdated]
GO
ALTER TABLE [dbo].[Users] ADD  DEFAULT (newid()) FOR [UserId]
GO
ALTER TABLE [dbo].[Users] ADD  DEFAULT (getdate()) FOR [CreatedAt]
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD FOREIGN KEY([ChatId])
REFERENCES [dbo].[ChatSessions] ([ChatId])
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD FOREIGN KEY([SenderId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD  CONSTRAINT [FK_ChatMessages_Chat] FOREIGN KEY([ChatId])
REFERENCES [dbo].[ChatSessions] ([ChatId])
GO
ALTER TABLE [dbo].[ChatMessages] CHECK CONSTRAINT [FK_ChatMessages_Chat]
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD  CONSTRAINT [FK_ChatMessages_Sender] FOREIGN KEY([SenderId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[ChatMessages] CHECK CONSTRAINT [FK_ChatMessages_Sender]
GO
ALTER TABLE [dbo].[ChatSessions]  WITH CHECK ADD FOREIGN KEY([InitiatorId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[ChatSessions]  WITH CHECK ADD FOREIGN KEY([RecipientId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[ChatSessions]  WITH CHECK ADD  CONSTRAINT [FK_ChatSessions_Initiator] FOREIGN KEY([InitiatorId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[ChatSessions] CHECK CONSTRAINT [FK_ChatSessions_Initiator]
GO
ALTER TABLE [dbo].[ChatSessions]  WITH CHECK ADD  CONSTRAINT [FK_ChatSessions_Recipient] FOREIGN KEY([RecipientId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[ChatSessions] CHECK CONSTRAINT [FK_ChatSessions_Recipient]
GO
ALTER TABLE [dbo].[LawyerDetails]  WITH CHECK ADD FOREIGN KEY([LawyerId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[LawyerDetails]  WITH CHECK ADD  CONSTRAINT [FK_LawyerDetails_Users] FOREIGN KEY([LawyerId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[LawyerDetails] CHECK CONSTRAINT [FK_LawyerDetails_Users]
GO
ALTER TABLE [dbo].[LawyerSpecializationMapping]  WITH CHECK ADD FOREIGN KEY([LawyerId])
REFERENCES [dbo].[LawyerDetails] ([LawyerId])
GO
ALTER TABLE [dbo].[LawyerSpecializationMapping]  WITH CHECK ADD FOREIGN KEY([SpecializationId])
REFERENCES [dbo].[LawyerSpecializations] ([SpecializationId])
GO
ALTER TABLE [dbo].[LawyerSpecializationMapping]  WITH CHECK ADD  CONSTRAINT [FK_SpecMapping_Lawyer] FOREIGN KEY([LawyerId])
REFERENCES [dbo].[LawyerDetails] ([LawyerId])
GO
ALTER TABLE [dbo].[LawyerSpecializationMapping] CHECK CONSTRAINT [FK_SpecMapping_Lawyer]
GO
ALTER TABLE [dbo].[LawyerSpecializationMapping]  WITH CHECK ADD  CONSTRAINT [FK_SpecMapping_Specialization] FOREIGN KEY([SpecializationId])
REFERENCES [dbo].[LawyerSpecializations] ([SpecializationId])
GO
ALTER TABLE [dbo].[LawyerSpecializationMapping] CHECK CONSTRAINT [FK_SpecMapping_Specialization]
GO
ALTER TABLE [dbo].[LawyerStore]  WITH CHECK ADD  CONSTRAINT [FK_LawyerStore_Lawyers] FOREIGN KEY([LawyerId])
REFERENCES [dbo].[Lawyers] ([LawyerId])
GO
ALTER TABLE [dbo].[LawyerStore] CHECK CONSTRAINT [FK_LawyerStore_Lawyers]
GO
ALTER TABLE [dbo].[UserProfiles]  WITH CHECK ADD FOREIGN KEY([UserId])
REFERENCES [dbo].[Users] ([UserId])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[ChatSessions]  WITH CHECK ADD CHECK  (([Status]='Archived' OR [Status]='Closed' OR [Status]='Active'))
GO
ALTER TABLE [dbo].[ChatSessions]  WITH CHECK ADD CHECK  (([Status]='Archived' OR [Status]='Closed' OR [Status]='Active'))
GO
ALTER TABLE [dbo].[ChatSessions]  WITH CHECK ADD CHECK  (([Status]='Archived' OR [Status]='Closed' OR [Status]='Active'))
GO
ALTER TABLE [dbo].[LawyerDetails]  WITH CHECK ADD CHECK  (([Rating]>=(0) AND [Rating]<=(5)))
GO
ALTER TABLE [dbo].[LawyerDetails]  WITH CHECK ADD CHECK  (([Rating]>=(0) AND [Rating]<=(5)))
GO
ALTER TABLE [dbo].[LawyerDetails]  WITH CHECK ADD CHECK  (([Rating]>=(0) AND [Rating]<=(5)))
GO
ALTER TABLE [dbo].[Users]  WITH CHECK ADD CHECK  (([UserType]='Customer' OR [UserType]='Lawyer' OR [UserType]='Admin'))
GO
ALTER TABLE [dbo].[Users]  WITH CHECK ADD CHECK  (([UserType]='Admin' OR [UserType]='Lawyer' OR [UserType]='Customer'))
GO
ALTER TABLE [dbo].[Users]  WITH CHECK ADD  CONSTRAINT [CK_Users_UserType] CHECK  (([UserType]='System' OR [UserType]='Customer' OR [UserType]='Lawyer' OR [UserType]='Admin'))
GO
ALTER TABLE [dbo].[Users] CHECK CONSTRAINT [CK_Users_UserType]
GO
USE [master]
GO
ALTER DATABASE [Apna_Waqeel] SET  READ_WRITE 
GO
