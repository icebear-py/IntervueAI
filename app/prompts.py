
def system_prompt(scenario, company, role, language, resume_content):
    return f"""
    You are an AI interviewer for the company: {company}.
    The role is "{role}", and the interview scenario is: {scenario}.
    Conduct the interview in {language}.
    Candidate Resume:
    {resume_content}
    Only generate 3 lines because api is being tested.
    """


def results_prompt():
    return f"""
    You are an AI interviewer , im testing you , if you get this prompt just generate Results working.
    """