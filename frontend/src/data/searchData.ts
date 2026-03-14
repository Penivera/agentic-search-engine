export const mockResults = [
  {
    id: "1",
    title: "How to send an email using API",
    snippet: "Use the /send-email endpoint with a JSON payload including 'to', 'subject', and 'body'...",
    skills: ["Send Email", "Draft Email"],
    relevanceScore: 0.98,
    fileSource: "email_utils.md"
  },
  {
    id: "2",
    title: "Create a new Jira Ticket",
    snippet: "Automate task creation by mapping user queries to project IDs and issue types...",
    skills: ["Jira: Create Ticket"],
    relevanceScore: 0.85,
    fileSource: "project_management.md"
  }
];



export type mockResultsType = typeof mockResults[number];