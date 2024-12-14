USE [master]
GO
/****** Object:  Database [AW_Database]    Script Date: 12/14/2024 9:29:22 AM ******/
CREATE DATABASE [AW_Database]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'AW_Database', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.NOUMAN\MSSQL\DATA\AW_Database.mdf' , SIZE = 8192KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'AW_Database_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.NOUMAN\MSSQL\DATA\AW_Database_log.ldf' , SIZE = 8192KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO
ALTER DATABASE [AW_Database] SET COMPATIBILITY_LEVEL = 160
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [AW_Database].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [AW_Database] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [AW_Database] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [AW_Database] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [AW_Database] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [AW_Database] SET ARITHABORT OFF 
GO
ALTER DATABASE [AW_Database] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [AW_Database] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [AW_Database] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [AW_Database] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [AW_Database] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [AW_Database] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [AW_Database] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [AW_Database] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [AW_Database] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [AW_Database] SET  DISABLE_BROKER 
GO
ALTER DATABASE [AW_Database] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [AW_Database] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [AW_Database] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [AW_Database] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [AW_Database] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [AW_Database] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [AW_Database] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [AW_Database] SET RECOVERY FULL 
GO
ALTER DATABASE [AW_Database] SET  MULTI_USER 
GO
ALTER DATABASE [AW_Database] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [AW_Database] SET DB_CHAINING OFF 
GO
ALTER DATABASE [AW_Database] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [AW_Database] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [AW_Database] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [AW_Database] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
EXEC sys.sp_db_vardecimal_storage_format N'AW_Database', N'ON'
GO
ALTER DATABASE [AW_Database] SET QUERY_STORE = ON
GO
ALTER DATABASE [AW_Database] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
USE [AW_Database]
GO
/****** Object:  Table [dbo].[Activities]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Activities](
	[ActivityId] [int] NOT NULL,
	[LawyerId] [int] NULL,
	[Activity] [nvarchar](500) NULL,
	[Time] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[ActivityId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Appointments]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Appointments](
	[AppointmentId] [int] NOT NULL,
	[LawyerId] [int] NULL,
	[ClientId] [int] NULL,
	[Date] [datetime] NULL,
	[Location] [nvarchar](200) NULL,
	[Purpose] [nvarchar](500) NULL,
PRIMARY KEY CLUSTERED 
(
	[AppointmentId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Cases]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Cases](
	[CaseId] [int] NOT NULL,
	[LawyerId] [int] NULL,
	[ClientId] [int] NULL,
	[CaseType] [nvarchar](100) NULL,
	[CaseStatus] [nvarchar](50) NULL,
	[StartDate] [date] NULL,
	[EndDate] [date] NULL,
PRIMARY KEY CLUSTERED 
(
	[CaseId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ChatMessages]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ChatMessages](
	[ChatId] [int] IDENTITY(1,1) NOT NULL,
	[SessionId] [int] NOT NULL,
	[Message] [nvarchar](max) NOT NULL,
	[Type] [nvarchar](50) NOT NULL,
	[Time] [datetime] NULL,
	[References] [nvarchar](max) NULL,
	[RecommendedLawyers] [nvarchar](max) NULL,
 CONSTRAINT [PK_ChatMessages] PRIMARY KEY CLUSTERED 
(
	[ChatId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Client]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Client](
	[ClientId] [int] NOT NULL,
	[FirstName] [nvarchar](50) NULL,
	[LastName] [nvarchar](50) NULL,
	[Email] [nvarchar](100) NULL,
	[Phone] [nvarchar](20) NULL,
	[Address] [nvarchar](200) NULL,
PRIMARY KEY CLUSTERED 
(
	[ClientId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Lawyer]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Lawyer](
	[LawyerId] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [int] NOT NULL,
	[CNIC] [nvarchar](20) NOT NULL,
	[LicenseNumber] [nvarchar](50) NOT NULL,
	[Location] [nvarchar](255) NOT NULL,
	[Paid] [bit] NULL,
	[ExpiryDate] [date] NULL,
	[Experience] [int] NOT NULL,
	[Recommended] [int] NULL,
	[Specialization] [nvarchar](100) NULL,
	[Contact] [nvarchar](20) NULL,
	[Email] [nvarchar](100) NULL,
	[TimesClicked] [int] NOT NULL,
	[TimesShown] [int] NOT NULL,
	[LastRecommended] [nvarchar](max) NULL,
	[RecommendationCount] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[LawyerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[CNIC] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[LawyerReview]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[LawyerReview](
	[ReviewId] [int] IDENTITY(1,1) NOT NULL,
	[LawyerId] [int] NOT NULL,
	[ClientId] [int] NOT NULL,
	[Stars] [int] NOT NULL,
	[ReviewMessage] [nvarchar](1000) NULL,
	[ReviewTime] [datetime] NOT NULL,
 CONSTRAINT [PK_LawyerReview] PRIMARY KEY CLUSTERED 
(
	[ReviewId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Sessions]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Sessions](
	[SessionId] [int] IDENTITY(1,1) NOT NULL,
	[UserId] [int] NOT NULL,
	[Time] [datetime] NULL,
	[Topic] [nvarchar](max) NOT NULL,
	[Active] [bit] NULL,
 CONSTRAINT [PK_Sessions_New] PRIMARY KEY CLUSTERED 
(
	[SessionId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Subscription]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Subscription](
	[SubsId] [int] IDENTITY(1,1) NOT NULL,
	[CurrentSubscription] [nvarchar](100) NOT NULL,
	[ExpiryDate] [date] NOT NULL,
	[RemainingCredits] [int] NULL,
	[UserId] [int] NULL,
	[StartDate] [datetime2](7) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[SubsId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[User]    Script Date: 12/14/2024 9:29:23 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[User](
	[UserId] [int] IDENTITY(1,1) NOT NULL,
	[Name] [nvarchar](100) NOT NULL,
	[Email] [nvarchar](255) NOT NULL,
	[Password] [nvarchar](255) NOT NULL,
	[Role] [nvarchar](50) NOT NULL,
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
/****** Object:  Index [IX_LawyerReview_LawyerId]    Script Date: 12/14/2024 9:29:23 AM ******/
CREATE NONCLUSTERED INDEX [IX_LawyerReview_LawyerId] ON [dbo].[LawyerReview]
(
	[LawyerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[ChatMessages] ADD  DEFAULT (getdate()) FOR [Time]
GO
ALTER TABLE [dbo].[Lawyer] ADD  DEFAULT ((0)) FOR [Paid]
GO
ALTER TABLE [dbo].[Lawyer] ADD  DEFAULT ((0)) FOR [Recommended]
GO
ALTER TABLE [dbo].[Lawyer] ADD  DEFAULT ((0)) FOR [TimesClicked]
GO
ALTER TABLE [dbo].[Lawyer] ADD  DEFAULT ((0)) FOR [TimesShown]
GO
ALTER TABLE [dbo].[Lawyer] ADD  DEFAULT ((0)) FOR [RecommendationCount]
GO
ALTER TABLE [dbo].[LawyerReview] ADD  DEFAULT (getdate()) FOR [ReviewTime]
GO
ALTER TABLE [dbo].[Sessions] ADD  DEFAULT (getdate()) FOR [Time]
GO
ALTER TABLE [dbo].[Sessions] ADD  DEFAULT ((1)) FOR [Active]
GO
ALTER TABLE [dbo].[Subscription] ADD  DEFAULT ((0)) FOR [RemainingCredits]
GO
ALTER TABLE [dbo].[Activities]  WITH CHECK ADD FOREIGN KEY([LawyerId])
REFERENCES [dbo].[Lawyer] ([LawyerId])
GO
ALTER TABLE [dbo].[Appointments]  WITH CHECK ADD FOREIGN KEY([ClientId])
REFERENCES [dbo].[Client] ([ClientId])
GO
ALTER TABLE [dbo].[Appointments]  WITH CHECK ADD FOREIGN KEY([LawyerId])
REFERENCES [dbo].[Lawyer] ([LawyerId])
GO
ALTER TABLE [dbo].[Cases]  WITH CHECK ADD FOREIGN KEY([ClientId])
REFERENCES [dbo].[Client] ([ClientId])
GO
ALTER TABLE [dbo].[Cases]  WITH CHECK ADD FOREIGN KEY([LawyerId])
REFERENCES [dbo].[Lawyer] ([LawyerId])
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD  CONSTRAINT [FK_ChatMessages_Sessions] FOREIGN KEY([SessionId])
REFERENCES [dbo].[Sessions] ([SessionId])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[ChatMessages] CHECK CONSTRAINT [FK_ChatMessages_Sessions]
GO
ALTER TABLE [dbo].[Lawyer]  WITH CHECK ADD  CONSTRAINT [FK_Lawyer_User] FOREIGN KEY([UserId])
REFERENCES [dbo].[User] ([UserId])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Lawyer] CHECK CONSTRAINT [FK_Lawyer_User]
GO
ALTER TABLE [dbo].[LawyerReview]  WITH CHECK ADD  CONSTRAINT [FK_LawyerReview_Client] FOREIGN KEY([ClientId])
REFERENCES [dbo].[User] ([UserId])
GO
ALTER TABLE [dbo].[LawyerReview] CHECK CONSTRAINT [FK_LawyerReview_Client]
GO
ALTER TABLE [dbo].[LawyerReview]  WITH CHECK ADD  CONSTRAINT [FK_LawyerReview_Lawyer] FOREIGN KEY([LawyerId])
REFERENCES [dbo].[User] ([UserId])
GO
ALTER TABLE [dbo].[LawyerReview] CHECK CONSTRAINT [FK_LawyerReview_Lawyer]
GO
ALTER TABLE [dbo].[Sessions]  WITH CHECK ADD  CONSTRAINT [FK_Sessions_User] FOREIGN KEY([UserId])
REFERENCES [dbo].[User] ([UserId])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[Sessions] CHECK CONSTRAINT [FK_Sessions_User]
GO
ALTER TABLE [dbo].[Subscription]  WITH CHECK ADD  CONSTRAINT [FK_Subscription_User] FOREIGN KEY([UserId])
REFERENCES [dbo].[User] ([UserId])
GO
ALTER TABLE [dbo].[Subscription] CHECK CONSTRAINT [FK_Subscription_User]
GO
ALTER TABLE [dbo].[ChatMessages]  WITH CHECK ADD  CONSTRAINT [CHK_ChatMessages_Type] CHECK  (([Type]=N'Human Message' OR [Type]=N'AI Message'))
GO
ALTER TABLE [dbo].[ChatMessages] CHECK CONSTRAINT [CHK_ChatMessages_Type]
GO
ALTER TABLE [dbo].[LawyerReview]  WITH CHECK ADD  CONSTRAINT [CHK_LawyerReview_Stars] CHECK  (([Stars]>=(1) AND [Stars]<=(5)))
GO
ALTER TABLE [dbo].[LawyerReview] CHECK CONSTRAINT [CHK_LawyerReview_Stars]
GO
ALTER TABLE [dbo].[User]  WITH CHECK ADD CHECK  (([Role]='system' OR [Role]='lawyer' OR [Role]='client'))
GO
USE [master]
GO
ALTER DATABASE [AW_Database] SET  READ_WRITE 
GO
