# Requirements Document

## Introduction

The Housing Evaluation System (Checklist.casa) is a mobile-first micro SaaS application that simplifies and standardizes the process of evaluating multiple housing options during in-person visits. The system enables individuals or teams to capture consistent information on-site, collaborate seamlessly, and make informed housing decisions through structured comparison tools.

## Glossary

- **Housing_Evaluation_System**: The complete web application for managing housing evaluation projects
- **Project**: A container that groups all visits and criteria for a specific housing search (e.g., "Q1 Move to San Jose")
- **Visit**: A record of evaluating a specific property, including assessments against defined criteria
- **Criteria**: Standardized evaluation parameters used to assess each property consistently
- **Assessment**: The recorded evaluation of a specific criteria for a particular visit
- **Project_Owner**: The user who created a project and has full administrative control
- **Collaborator**: A user invited to participate in a project with editing permissions
- **Active_Project**: A project currently accepting new visits and edits
- **Finished_Project**: A completed project that is read-only and archived

## Requirements

### Requirement 1

**User Story:** As a house hunter, I want to create evaluation projects so that I can organize my housing search activities.

#### Acceptance Criteria

1. THE Housing_Evaluation_System SHALL allow authenticated users to create new projects with a descriptive name
2. WHEN a user creates a project, THE Housing_Evaluation_System SHALL automatically assign them as the Project_Owner
3. THE Housing_Evaluation_System SHALL set newly created projects to Active_Project status
4. THE Housing_Evaluation_System SHALL record the creation timestamp for each project
5. THE Housing_Evaluation_System SHALL display all user projects on a dashboard interface

### Requirement 2

**User Story:** As a project owner, I want to invite collaborators to my project so that my partner or team can help evaluate properties.

#### Acceptance Criteria

1. THE Housing_Evaluation_System SHALL allow Project_Owner to invite users by email address
2. WHEN an invitation is sent, THE Housing_Evaluation_System SHALL send an email with a project invitation link
3. IF the invited email is not registered, THE Housing_Evaluation_System SHALL allow account creation through the invitation link
4. WHEN an invitation is accepted, THE Housing_Evaluation_System SHALL add the user as a Collaborator to the project
5. THE Housing_Evaluation_System SHALL display all project Collaborators to the Project_Owner

### Requirement 3

**User Story:** As a project member, I want to define evaluation criteria so that I can consistently assess each property I visit.

#### Acceptance Criteria

1. THE Housing_Evaluation_System SHALL allow project members to create custom Criteria with name and type
2. THE Housing_Evaluation_System SHALL support boolean, numeric, text, and rating Criteria types
3. THE Housing_Evaluation_System SHALL allow project members to set optional weight values for Criteria
4. THE Housing_Evaluation_System SHALL allow project members to reorder Criteria for consistent presentation
5. THE Housing_Evaluation_System SHALL provide default Criteria templates for common housing evaluation needs

### Requirement 4

**User Story:** As a project member, I want to log property visits so that I can capture detailed information during my housing search.

#### Acceptance Criteria

1. THE Housing_Evaluation_System SHALL provide a mobile-optimized form for creating new Visit records
2. THE Housing_Evaluation_System SHALL capture basic Visit information including name, address, realtor contact, and visit date
3. THE Housing_Evaluation_System SHALL allow users to upload up to 5 photos per Visit
4. THE Housing_Evaluation_System SHALL present all project Criteria for Assessment during Visit creation
5. THE Housing_Evaluation_System SHALL allow users to add free-form notes to each Visit

### Requirement 5

**User Story:** As a project member, I want to assess properties against my criteria so that I can make objective comparisons.

#### Acceptance Criteria

1. THE Housing_Evaluation_System SHALL create Assessment records linking each Visit to project Criteria
2. THE Housing_Evaluation_System SHALL enforce data type validation for Assessment values based on Criteria type
3. WHEN a user evaluates a property, THE Housing_Evaluation_System SHALL present Criteria in the defined order
4. THE Housing_Evaluation_System SHALL allow users to skip optional Criteria during Assessment
5. THE Housing_Evaluation_System SHALL save Assessment progress automatically during Visit creation

### Requirement 6

**User Story:** As a project member, I want to compare all my property visits so that I can identify the best options.

#### Acceptance Criteria

1. THE Housing_Evaluation_System SHALL display a comparison table with Visit records as rows and Criteria as columns
2. THE Housing_Evaluation_System SHALL populate table cells with corresponding Assessment values
3. THE Housing_Evaluation_System SHALL provide sorting functionality for each Criteria column
4. THE Housing_Evaluation_System SHALL apply color coding to highlight best and worst Assessment values
5. THE Housing_Evaluation_System SHALL allow filtering of Visit records based on Assessment criteria

### Requirement 7

**User Story:** As a project owner, I want to finish completed projects so that I can archive them and start new searches.

#### Acceptance Criteria

1. THE Housing_Evaluation_System SHALL allow only Project_Owner to mark projects as Finished_Project
2. WHEN a project is finished, THE Housing_Evaluation_System SHALL record the completion timestamp
3. THE Housing_Evaluation_System SHALL prevent all editing operations on Finished_Project records
4. THE Housing_Evaluation_System SHALL maintain read-only access to Finished_Project data for all members
5. THE Housing_Evaluation_System SHALL display Finished_Project status clearly in the user interface

### Requirement 8

**User Story:** As a project member, I want to export my evaluation data so that I can share results or keep records outside the system.

#### Acceptance Criteria

1. THE Housing_Evaluation_System SHALL generate CSV exports of the comparison table data
2. THE Housing_Evaluation_System SHALL generate PDF exports of the comparison table with basic formatting
3. THE Housing_Evaluation_System SHALL include all Visit and Assessment data in exports
4. THE Housing_Evaluation_System SHALL allow export generation for both Active_Project and Finished_Project records
5. THE Housing_Evaluation_System SHALL include project metadata in exported files

### Requirement 9

**User Story:** As a user, I want secure access to my projects so that my housing search data remains private.

#### Acceptance Criteria

1. THE Housing_Evaluation_System SHALL require user authentication for all project operations
2. THE Housing_Evaluation_System SHALL restrict project access to Project_Owner and invited Collaborators only
3. THE Housing_Evaluation_System SHALL use Django Allauth for user registration and authentication
4. THE Housing_Evaluation_System SHALL maintain secure session management for authenticated users
5. THE Housing_Evaluation_System SHALL deny access to unauthorized users attempting to view project data

### Requirement 10

**User Story:** As a house hunter, I want to have the setting available to receive a confirmation email everytime I upload information about a new home

1. THE Housing_Evaluation_System SHALL send a confirmation email to the user after uploading information about a new home
2. THE Housing_Evaluation_System SHALL allow the user to opt out of receiving confirmation emails
3. THE Housing_Evaluation_System SHALL have the default setting for receiving confirmation emails enabled
4. THE Housing_Evaluation_System SHALL allow the user to change the default setting for receiving confirmation emails