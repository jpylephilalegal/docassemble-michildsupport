# docassemble.michildsupport

This is a [docassemble] [add-on package] for determining child support
obligations in Michigan using the [MiChildSupport Calculator].

It contains a sample interview, [childsupport.yml], that asks the user
questions about parents, guardians, children, income, expenses, and
health insurance coverage.  After the information is gathered, the
interview makes the user wait while it runs the information through
the [MiChildSupport Calculator].  When that process is completed, the
interview tells the user who owes how much to whom.

The [childsupport.yml] interview is intended to be a starting point
for guided interviews that use the [MiChildSupport Calculator].

## How it works

Behind the scenes, the [childsupport.yml] interview performs "document
assembly" using the template [calculate.feature].  This isn't ordinary
document assembly that creates a Word file or a PDF file; rather, it
assembles a text file that looks something like this:

```
Feature: Filling out the child support calculator
  I want to calculate child support using the Michigan Child Support Calculator.

  Scenario: Calculate child support for the interviewee
    Given I start the child support calculator
    Then I should see the phrase "Welcome to the MiChildSupport Calculator"
    And I click the button "Continue"
    Then I should see the phrase "Getting Started"
    And I select "Two Parents" as the "Select Child Support Group:"
    And I select "One Child" as the "Select Number of Child Support Children:"
    And I wait 1 second
    And I set the first "First Name:" to "John"
    And I set the first "Last Name:" to "Smith"
    And I set the second "First Name:" to "Jane"
    And I set the second "Last Name:" to "Smith"
    And I set the fourth "First Name:" to "Thomas"
    And I set the fourth "Last Name:" to "Smith"
    And I set the first "Date of Birth:" to "04/04/2006"
    And I select "2021" as the "Select Tax Year:"
    And I set "Court Case Number:" to "05-3432322"
    And I select "Huron" as the "Select Court Case County:"
    And I set "Description:" to "Michigan Legal Help child support calculation"
    And I click the button "Continue"
    Then I should see the phrase "Children Information for: JOHN SMITH"
    And I set the field "childParticipantList[0].overnightsSpentParentA" to "160.0"
    And I check the checkbox field "childParticipantList[0].onCalculationInd"
    And I select "2" as the field "additionalMinorChildren"
    And I click the button "Continue"
    Then I should see the phrase "Financial Information for: JOHN SMITH"
    And I select "Employer Wages" as the field "incomeRecord[0].incomeTypeCode"
    And I wait 1 second
    And I check the checkbox field "incomeRecord[0].potentialIncome"
    And I set the field "incomeRecord[0].employer" to "ABC Inc."
    And I set the field "incomeRecord[0].grossWageFrequency.sourceAmount" to "3200.0"
    And I select "Monthly" as the field "incomeRecord[0].grossWageFrequency.frequencyCD"
    And I set the field "incomeRecord[0].overTimeFrequency.sourceAmount" to "0.0"
    And I select "Monthly" as the field "incomeRecord[0].overTimeFrequency.frequencyCD"
    And I set the field "incomeRecord[0].shiftPremiumFrequency.sourceAmount" to "0.0"
    And I select "Monthly" as the field "incomeRecord[0].shiftPremiumFrequency.frequencyCD"
    And I set the field "incomeRecord[0].employeeMandatoryAmt" to "5.0"
    And I click the button "Add a Source of Income"
    And I wait 1 second
    And I select "Adoption Subsidy" as the field "incomeRecord[1].incomeTypeCode"
    And I wait 1 second
    And I check the checkbox field "incomeRecord[1].potentialIncome"
    And I set the field "incomeRecord[1].grossWageFrequency.sourceAmount" to "32.0"
    And I select "Monthly" as the field "incomeRecord[1].grossWageFrequency.frequencyCD"
    And I set the field "calcDeduction.numIRSExemptions" to "2"
    And I select "Head of Household" as the field "calcDeduction.irsFilingStatus"
    And I select "Grand Rapids" as the field "calcDeduction.cityOfResidence"
    And I select "Hamtramck" as the field "calcDeduction.cityOfEmployment"
    And I select "I know the tax amounts and will enter them" as the id "selectHowToEnterTax"
    And I unfocus
    And I wait 3 seconds
    And I select "Annually" as the field "calcDeduction.frequency.frequencyCD"
    And I set the field "calcDeduction.fedIncomeTaxOvrdInput" to "1000.0"
    And I set the field "calcDeduction.stateIncomeTaxOvrdInput" to "200.0"
    And I set the field "calcDeduction.ficaTaxOvrdInput" to "10.0"
    And I set the field "calcDeduction.resCityTaxOvrdInput" to "0.0"
    And I set the field "calcDeduction.nonResCityTaxOvrdInput" to "178.0"
    And I click the button "Add an Additional Deduction"
    And I wait 1 second
    And I select "Required Union Dues" as the field "calcAdditionalDeductions[0].deductionType"
    And I set the field "calcAdditionalDeductions[0].frequency.sourceAmount" to "100.0"
    And I select "Monthly" as the field "calcAdditionalDeductions[0].frequency.frequencyCD"
    And I click the button "Add an Additional Deduction"
    And I wait 1 second
    And I select "Spousal Support Paid to Another Party" as the field "calcAdditionalDeductions[1].deductionType"
    And I set the field "calcAdditionalDeductions[1].frequency.sourceAmount" to "10.0"
    And I select "Weekly" as the field "calcAdditionalDeductions[1].frequency.frequencyCD"
    And I click the button "Continue"
    And I wait 2 seconds
    Then I should see the phrase "Child Care Information for: JOHN SMITH"
    And I click the button "Add a Child Care Expense"
    And I wait 1 second
    And I select "All" as the field "childCareExpenses[0].childId"
    And I select "10" as the field "childCareExpenses[0].numberOfChildCareMonths"
    And I set the field "childCareExpenses[0].guidelineFrequency.sourceAmount" to "100.0"
    And I select "Monthly" as the field "childCareExpenses[0].guidelineFrequency.frequencyCD"
    And I check the checkbox field "childCareExpenses[0].potentialChildCareInd"
    And I check the checkbox field "childCareCredits.overrideInd"
    And I set the field "childCareCredits.ccTaxCreditsFrequency.sourceAmount" to "152.0"
    And I select "Monthly" as the field "childCareCredits.ccTaxCreditsFrequency.frequencyCD"
    And I set the field "childCareCredits.ccSubsidiesFrequency.sourceAmount" to "75.0"
    And I select "Monthly" as the field "childCareCredits.ccSubsidiesFrequency.frequencyCD"
    And I check the checkbox field "childParticipants[0].childCareReimOverrideEndDateInd"
    And I wait 1 second
    And I set the field "childParticipants[0].childCareReimOverrideEndDate" to "05/05/2024"
    And I click the button "Continue"
    Then I should see the phrase "Medical Information for: JOHN SMITH"
    And I set the field "calcMedIns.medicalInsFreq.sourceAmount" to "56.0"
    And I select "Monthly" as the field "calcMedIns.medicalInsFreq.frequencyCD"
    And I select "No" as the field "calcMedIns.healthInsProvidedOtherInd"
    And I set the field "calcMedIns.childerenOnCalculationCovered" to "1"
    And I set the field "calcMedIns.additionalQualifiedChilderenCovered" to "0"
    And I set the field "calcMedIns.additonalPeopleCovered" to "0"
    And I click the button "Add an additional Out-of-Pocket Medical Expense"
    And I select "All" as the field "additionalMedicalExpenses[0].childId"
    And I set the field "additionalMedicalExpenses[0].addMedicalInsFreq.sourceAmount" to "566.0"
    And I select "Monthly" as the field "additionalMedicalExpenses[0].addMedicalInsFreq.frequencyCD"
    And I select "Yes" as the field "calcMedIns.reaCostOfHcInd"
    And I select "Yes" as the field "recommendedToProvide"
    And I select "Yes" as the field "calcMedIns.incurMedicalExpenseInd"
    And I click the button "Continue"
    Then I should see the phrase "Children Information for: JANE SMITH"
    And I set the field "childParticipantList[0].overnightsSpentParentB" to "205.0"
    And I check the checkbox field "childParticipantList[0].onCalculationInd"
    And I select "2" as the field "additionalMinorChildren"
    And I click the button "Continue"
    Then I should see the phrase "Financial Information for: JANE SMITH"
    And I select "Employer Wages" as the field "incomeRecord[0].incomeTypeCode"
    And I wait 1 second
    And I check the checkbox field "incomeRecord[0].potentialIncome"
    And I set the field "incomeRecord[0].employer" to "DEF Inc."
    And I set the field "incomeRecord[0].grossWageFrequency.sourceAmount" to "3000.0"
    And I select "Monthly" as the field "incomeRecord[0].grossWageFrequency.frequencyCD"
    And I set the field "incomeRecord[0].overTimeFrequency.sourceAmount" to "100.0"
    And I select "Monthly" as the field "incomeRecord[0].overTimeFrequency.frequencyCD"
    And I set the field "incomeRecord[0].shiftPremiumFrequency.sourceAmount" to "0.0"
    And I select "Monthly" as the field "incomeRecord[0].shiftPremiumFrequency.frequencyCD"
    And I set the field "incomeRecord[0].employeeMandatoryAmt" to "0"
    And I click the button "Add a Source of Income"
    And I wait 1 second
    And I select "Allowance for Rent" as the field "incomeRecord[1].incomeTypeCode"
    And I wait 1 second
    And I check the checkbox field "incomeRecord[1].potentialIncome"
    And I set the field "incomeRecord[1].grossWageFrequency.sourceAmount" to "15.0"
    And I select "Weekly" as the field "incomeRecord[1].grossWageFrequency.frequencyCD"
    And I set the field "calcDeduction.numIRSExemptions" to "1"
    And I select "Single" as the field "calcDeduction.irsFilingStatus"
    And I select "Grayling" as the field "calcDeduction.cityOfResidence"
    And I select "Lapeer" as the field "calcDeduction.cityOfEmployment"
    And I select "I don't know the tax amounts; estimate monthly taxes for me" as the id "selectHowToEnterTax"
    And I unfocus
    And I wait 3 seconds
    And I click the button "Add an Additional Deduction"
    And I wait 1 second
    And I select "Life Insurance - Child Beneficiary" as the field "calcAdditionalDeductions[0].deductionType"
    And I set the field "calcAdditionalDeductions[0].frequency.sourceAmount" to "50.0"
    And I select "Monthly" as the field "calcAdditionalDeductions[0].frequency.frequencyCD"
    And I click the button "Continue"
    And I wait 2 seconds
    Then I should see the phrase "Child Care Information for: JANE SMITH"
    And I click the button "Add a Child Care Expense"
    And I wait 1 second
    And I select "All" as the field "childCareExpenses[0].childId"
    And I select "2" as the field "childCareExpenses[0].numberOfChildCareMonths"
    And I set the field "childCareExpenses[0].guidelineFrequency.sourceAmount" to "230.0"
    And I select "Monthly" as the field "childCareExpenses[0].guidelineFrequency.frequencyCD"
    And I check the checkbox field "childCareExpenses[0].potentialChildCareInd"
    And I check the checkbox field "childCareCredits.overrideInd"
    And I set the field "childCareCredits.ccTaxCreditsFrequency.sourceAmount" to "51.0"
    And I select "Monthly" as the field "childCareCredits.ccTaxCreditsFrequency.frequencyCD"
    And I set the field "childCareCredits.ccSubsidiesFrequency.sourceAmount" to "98.0"
    And I select "Monthly" as the field "childCareCredits.ccSubsidiesFrequency.frequencyCD"
    And I check the checkbox field "childParticipants[0].childCareReimOverrideEndDateInd"
    And I wait 1 second
    And I set the field "childParticipants[0].childCareReimOverrideEndDate" to "05/05/2024"
    And I click the button "Continue"
    Then I should see the phrase "Medical Information for: JANE SMITH"
    And I set the field "calcMedIns.medicalInsFreq.sourceAmount" to "51.0"
    And I select "Monthly" as the field "calcMedIns.medicalInsFreq.frequencyCD"
    And I select "No" as the field "calcMedIns.healthInsProvidedOtherInd"
    And I set the field "calcMedIns.childerenOnCalculationCovered" to "1"
    And I set the field "calcMedIns.additionalQualifiedChilderenCovered" to "0"
    And I set the field "calcMedIns.additonalPeopleCovered" to "0"
    And I select "Yes" as the field "calcMedIns.reaCostOfHcInd"
    And I select "No" as the field "recommendedToProvide"
    And I select "No" as the field "calcMedIns.incurMedicalExpenseInd"
    And I click the button "Continue"
    Then I should see the phrase "Results"
    And I save a screenshot to "output.png"
    And I save the HTML of the page to "output.html"
    And I save the DOM of the page to "dom.html"
```

This text file is a list of instructions for entering information into
the [MiChildSupport Calculator].  The instructions are written in a
language called [Gherkin].  In the interview, the process of
assembling this "document" triggers all of the necessary questions
about parents, guardians, children, income, expenses, health
insurance, etc.

When this "document" has been assembled, it is sent to a web browser
automation application ([aloe]), which launches Chrome on the
[docassemble] server (out of sight of the user).  The web browser
automation software follows each instruction step-by-step; it
effectively types letters and numbers into the [MiChildSupport
Calculator] web site and clicks buttons, just like a human user of the
web site would.  When the last page of the web site is reached, the
information on that final screen is [scraped] and placed into a data
structure, which is saved in the "interview answers" of the guided
interview, so that the logic of the guided interview can do things
with it.

The [Gherkin] language is intended to be [human-readable] and
[machine-readable] at the same time.  It is primarily used for
[acceptance testing] and [Behavior-Driven Development], which is why
it uses words like "Feature" and "Scenario."  Using [Gherkin] for
running a child support calculator is a little out-of-the-ordinary,
but it is effective.  The fact that the language is intended to be
[human-readable] means that it is easier for non-programmers to
understand it.

Some of the steps are more readable than others.  The step `And I
select "Two Parents" as the "Select Child Support Group:"` is pretty
understandable to someone who has used the [MiChildSupport
Calculator], but the step `And I check the checkbox field
"childCareCredits.overrideInd"` is less self-explanatory.
Unfortunately, the [MiChildSupport Calculator] has complex and
repetitive HTML, so it was not feasible to drive it only with "steps"
that refer to labels on the screen.  Instead, I had to identify fields
using the hidden `name` attribute, which I found by right-clicking
each field and choosing "Inspect."  Each line of the instructions
needs to match the pattern of a "step" in the [step definition file].

The code for "scraping" information from the final screen is pretty
complex; see the `extract_data()` function in [misc.py] if you want to
see it.

The sample interview [childsupport.yml] is designed so that a subject
matter expert can make language changes to it using GitHub's "edit"
feature in combination with Ctrl-f to find the phrases they want to
change.  The subject matter expert can skip over whatever they don't
understand.  There is no way they can cause any harm to the code
because GitHub keeps a careful record of all changes and a developer
will need to review changes before accepting them.  The
[childsupport.yml] file is in the [YAML] format and most text items
within the [YAML] are written in the [Markdown] language.  The
templating syntax you see (`${ ... }`, `% endif`, etc.) is the
language [Mako].  [YAML] is a good language because it uses a minimum
of punctuation and it is easy to read and understand; on the other
hand, this means it is very picky about whitespace.  [Markdown] is
also easy to use; most of the time it looks like like plain text.  It
has a few formatting features, like the ability to express hyperlinks.

Structural changes to the interview would need to be made by a
[docassemble] developer.  Subject matter experts could request such
changes using the GitHub "issues" system.

In the [childsupport.yml] interview, the order of the questions is
entirely determined by the [calculate.feature] template file.  As a
result, the interview flow is very similar to that of the
[MiChildSupport Calculator].  It is possible to [change the order of
questions] if you desire.

The code for running web browser automation is in the [misc.py] file.
This Python module file is included in the [childsupport.yml]
interview using a [`modules`] block.  The web browser automation
process is launched with the `run_automation()` function.  Since the
process can take a minute, the code is called from a [background task]
and the user looks at a waiting screen until the process has
completed.  Alternatively, you could use this time to ask the user
additional questions that are necessary for your interview but are not
necessary for the [MiChildSupport Calculator].  If the background
process is successful, the variable `success` is set the `True` and
the variable `output_data` is set to a Python data structure
containing information from the final screen.  Processing this
information can get complicated because sometimes the [MiChildSupport
Calculator] produces three different alternative results.

## Hosting

Deploying a guided interview that uses `docassemble.michildsupport`
will require self-hosting a [docassemble] server.  Any machine capable
of running [Docker] can run [docassemble], but most people use a
virtual machine in the cloud, such as an [EC2 instance] running
[Ubuntu].  Machines cost more when they have more resources, but it is
important to use a machine that meets the [minimum system
requirements].  I recommend using [S3] as a storage mechanism.

## Author

Jonathan Pyle, jpyle@philalegal.org, 215-981-3843

[S3]: https://docassemble.org/docs/docker.html#persistent%20s3
[minimum system requirements]: https://docassemble.org/docs/docker.html#install
[EC2 instance]: https://aws.amazon.com/ec2/
[Ubuntu]: https://aws.amazon.com/marketplace/pp/B087QQNGF1
[Docker]: https://www.docker.com/
[change the order of questions]: https://docassemble.org/docs/logic.html
[Mako]: http://www.makotemplates.org/
[YAML]: https://en.wikipedia.org/wiki/YAML
[Markdown]: https://daringfireball.net/projects/markdown/
[misc.py]: https://github.com/jpylephilalegal/docassemble-michildsupport/blob/master/docassemble/michildsupport/misc.py
[step definition file]: https://github.com/jpylephilalegal/docassemble-michildsupport/blob/master/docassemble/michildsupport/data/sources/features/steps/supportcalc.py
[Behavior-Driven Development]: https://en.wikipedia.org/wiki/Behavior-driven_development
[acceptance testing]: https://en.wikipedia.org/wiki/Acceptance_testing
[human-readable]: https://en.wikipedia.org/wiki/Human-readable_medium
[machine-readable]: https://en.wikipedia.org/wiki/Machine-readable_data
[Gherkin]: https://en.wikipedia.org/wiki/Cucumber_(software)#Gherkin_language
[calculate.feature]: https://github.com/jpylephilalegal/docassemble-michildsupport/blob/master/docassemble/michildsupport/data/questions/childsupport.yml
[childsupport.yml]: https://github.com/jpylephilalegal/docassemble-michildsupport/blob/master/docassemble/michildsupport/data/templates/calculate.feature
[MiChildSupport Calculator]: https://micase.state.mi.us/calculatorapp/public/gettingStarted/load.html
[docassemble]: https://docassemble.org
[add-on package]: https://docassemble.org/docs/packages.html
[aloe]: https://aloe.readthedocs.io/en/latest/
[scraped]: https://en.wikipedia.org/wiki/Web_scraping
[`modules`]: https://docassemble.org/docs/initial.html#modules
[background task]: https://docassemble.org/docs/background.html#background
