CREATE DATABASE [Apna_Waqeel]
GO
USE [Apna_Waqeel]
GO

-- Core User Tables
CREATE TABLE [Users] (
    [UserId] [uniqueidentifier] PRIMARY KEY DEFAULT newid(),
    [UserName] [nvarchar](255) NOT NULL,
    [Email] [nvarchar](255) NOT NULL UNIQUE,
    [CreatedAt] [datetime2](7) DEFAULT getdate(),
    [UserType] [nvarchar](50) NOT NULL CHECK ([UserType] IN ('Admin', 'Lawyer', 'Customer')),
    [PasswordHash] [nvarchar](255) NOT NULL
)
GO

CREATE TABLE [UserProfiles] (
    [ProfileId] [uniqueidentifier] PRIMARY KEY DEFAULT newid(),
    [UserId] [uniqueidentifier] NOT NULL,
    [ContactNumber] [nvarchar](20),
    [Address] [nvarchar](500),
    [LastUpdated] [datetime2](7) DEFAULT getdate(),
    FOREIGN KEY ([UserId]) REFERENCES [Users]([UserId]) ON DELETE CASCADE
)
GO

-- Lawyer Related Tables
CREATE TABLE [LawyerDetails] (
    [LawyerId] [uniqueidentifier] PRIMARY KEY,
    [Specialization] [nvarchar](100) NOT NULL,
    [Experience] [int] NOT NULL,
    [LicenseNumber] [nvarchar](50) UNIQUE NOT NULL,
    [Rating] [decimal](3,2) CHECK ([Rating] >= 0 AND [Rating] <= 5),
    [Location] [nvarchar](255) NOT NULL,
    FOREIGN KEY ([LawyerId]) REFERENCES [Users]([UserId])
)
GO

CREATE TABLE [LawyerSpecializations] (
    [SpecializationId] [uniqueidentifier] PRIMARY KEY DEFAULT newid(),
    [Name] [nvarchar](100) UNIQUE NOT NULL
)
GO

CREATE TABLE [LawyerSpecializationMapping] (
    [LawyerId] [uniqueidentifier],
    [SpecializationId] [uniqueidentifier],
    PRIMARY KEY ([LawyerId], [SpecializationId]),
    FOREIGN KEY ([LawyerId]) REFERENCES [LawyerDetails]([LawyerId]),
    FOREIGN KEY ([SpecializationId]) REFERENCES [LawyerSpecializations]([SpecializationId])
)
GO

-- Chat Related Tables
CREATE TABLE [ChatSessions] (
    [ChatId] [uniqueidentifier] PRIMARY KEY DEFAULT newid(),
    [InitiatorId] [uniqueidentifier] NOT NULL,
    [RecipientId] [uniqueidentifier] NOT NULL,
    [StartTime] [datetime2](7) DEFAULT getdate(),
    [EndTime] [datetime2](7),
    [Status] [nvarchar](20) CHECK ([Status] IN ('Active', 'Closed', 'Archived')),
    FOREIGN KEY ([InitiatorId]) REFERENCES [Users]([UserId]),
    FOREIGN KEY ([RecipientId]) REFERENCES [Users]([UserId])
)
GO

CREATE TABLE [ChatMessages] (
    [MessageId] [uniqueidentifier] PRIMARY KEY DEFAULT newid(),
    [ChatId] [uniqueidentifier] NOT NULL,
    [SenderId] [uniqueidentifier] NOT NULL,
    [Message] [nvarchar](max) NOT NULL,
    [MessageType] [nvarchar](50) NOT NULL,
    [Timestamp] [datetime2](7) DEFAULT getdate(),
    FOREIGN KEY ([ChatId]) REFERENCES [ChatSessions]([ChatId]),
    FOREIGN KEY ([SenderId]) REFERENCES [Users]([UserId])
)
GO

-- Create indexes for better performance
CREATE INDEX [IX_ChatMessages_ChatId] ON [ChatMessages]([ChatId])
GO
CREATE INDEX [IX_ChatMessages_UserId_ChatId] ON [ChatMessages]([SenderId], [ChatId])
GO
GO
USE [Apna_Waqeel]
GO
/****** Object:  Table [dbo].[ChatMessages]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[ChatSessions]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[ChatTopics]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[Customers]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[LawyerDetails]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[Lawyers]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[LawyerSpecializationMapping]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[LawyerSpecializations]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[LawyerStore]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[Metadata]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[Sessions]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[UserProfiles]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[Users]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Table [dbo].[UserSessions]    Script Date: 12/8/2024 1:50:42 PM ******/
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
/****** Object:  Index [IX_ChatMessages_ChatId]    Script Date: 12/8/2024 1:50:42 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatMessages_ChatId] ON [dbo].[ChatMessages]
(
	[ChatId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_ChatMessages_UserId_ChatId]    Script Date: 12/8/2024 1:50:42 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatMessages_UserId_ChatId] ON [dbo].[ChatMessages]
(
	[SenderId] ASC,
	[ChatId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_ChatSessions_Users]    Script Date: 12/8/2024 1:50:42 PM ******/
CREATE NONCLUSTERED INDEX [IX_ChatSessions_Users] ON [dbo].[ChatSessions]
(
	[InitiatorId] ASC,
	[RecipientId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IX_LawyerDetails_Specialization]    Script Date: 12/8/2024 1:50:42 PM ******/
CREATE NONCLUSTERED INDEX [IX_LawyerDetails_Specialization] ON [dbo].[LawyerDetails]
(
	[Specialization] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_LawyerStore_LawyerId]    Script Date: 12/8/2024 1:50:42 PM ******/
CREATE NONCLUSTERED INDEX [IX_LawyerStore_LawyerId] ON [dbo].[LawyerStore]
(
	[LawyerId] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IX_UserProfiles_UserId]    Script Date: 12/8/2024 1:50:42 PM ******/
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
ALTER TABLE [dbo].[LawyerDetails]  WITH CHECK ADD  CONSTRAINT [FK_LawyerDetails_Users] FOREIGN KEY([LawyerId])
REFERENCES [dbo].[Users] ([UserId])
GO
ALTER TABLE [dbo].[LawyerDetails] CHECK CONSTRAINT [FK_LawyerDetails_Users]
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
ALTER TABLE [dbo].[UserProfiles]  WITH CHECK ADD  CONSTRAINT [FK_UserProfiles_Users] FOREIGN KEY([UserId])
REFERENCES [dbo].[Users] ([UserId])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[UserProfiles] CHECK CONSTRAINT [FK_UserProfiles_Users]
GO
ALTER TABLE [dbo].[ChatSessions]  WITH CHECK ADD CHECK  (([Status]='Archived' OR [Status]='Closed' OR [Status]='Active'))
GO
ALTER TABLE [dbo].[LawyerDetails]  WITH CHECK ADD CHECK  (([Rating]>=(0) AND [Rating]<=(5)))
GO
ALTER TABLE [dbo].[Users]  WITH CHECK ADD CHECK  (([UserType]='Admin' OR [UserType]='Lawyer' OR [UserType]='Customer'))
GO
USE [master]
GO
ALTER DATABASE [Apna_Waqeel] SET  READ_WRITE 
GO
