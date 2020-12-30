Feature: Filling out the child support calculator
  I want to calculate child support using the Michigan Child Support Calculator.

  Scenario: Calculate child support for the interviewee
    Given I start the child support calculator
    Then I should see the phrase "Welcome to the MiChildSupport Calculator"
    And I click the button "Continue"
    Then I should see the phrase "Getting Started"
% if child_support_group == 'AB':
    And I select "Two Parents" as the "Select Child Support Group:"
% elif child_support_group == 'AC':
    And I select "One Parent and a Non-Parent Custodian" as the "Select Child Support Group:"
% else:
    And I select "Two Parents and a Non-Parent Custodian" as the "Select Child Support Group:"
% endif
% if children.target_number == 1:
    And I select "One Child" as the "Select Number of Child Support Children:"
% elif children.target_number == 2:
    And I select "Two Children" as the "Select Number of Child Support Children:"
% elif children.target_number == 3:
    And I select "Three Children" as the "Select Number of Child Support Children:"
% elif children.target_number == 4:
    And I select "Four Children" as the "Select Number of Child Support Children:"
% elif children.target_number == 5:
    And I select "Five Children" as the "Select Number of Child Support Children:"
% endif
    And I wait 1 second
% for party_code in 'ABC':
  % if party_code in parents:
    And I set the ${ ordinal(loop.index) } "First Name:" to "${ parents[party_code].name.first }"
    And I set the ${ ordinal(loop.index) } "Last Name:" to "${ parents[party_code].name.last }"
  % endif
% endfor
% for child in children:
    And I set the ${ ordinal(3 + loop.index) } "First Name:" to "${ child.name.first }"
    And I set the ${ ordinal(3 + loop.index) } "Last Name:" to "${ child.name.last }"
    And I set the ${ ordinal(loop.index) } "Date of Birth:" to "${ child.birthdate.format('MM/dd/yyyy') }"
  % if 'C' in child_support_group:
    % if child.lives_with_non_parent_custodian:
    And I check the checkbox field "childParticipantList[${ loop.index }].livingWithNonParentCustInd"
    % else:
    And I uncheck the checkbox field "childParticipantList[${ loop.index }].livingWithNonParentCustInd"
    % endif
  % endif
% endfor
    And I select "${ tax_year }" as the "Select Tax Year:"
  % if has_a_court_case:
    And I set "Court Case Number:" to "${ court_case_number }"
    And I select "${ court_case_county }" as the "Select Court Case County:"
  % endif
    And I set "Description:" to "${ calculation_description }"
    And I click the button "Continue"
% for parent_code, parent in parents.items():
  % if parent_code != 'C':
    Then I should see the phrase "Children Information for: ${ parent.name.full().upper() }"
    % if 'C' in child_support_group:
      % for overnight in parent.overnights:
        % if not children[loop.index].lives_with_non_parent_custodian:
    And I set the field "childParticipantList[${ loop.index }].overnightsSpentParent${ parent_code }" to "${ overnight.days }"
        % endif
        % if overnight.include:
    And I check the checkbox field "childParticipantList[${ loop.index }].onCalculationInd"
        % else:
    And I uncheck the checkbox field "childParticipantList[${ loop.index }].onCalculationInd"
        % endif
      % endfor
    % else:
      % for overnight in parent.overnights:
    And I set the field "childParticipantList[${ loop.index }].overnightsSpentParent${ parent_code }" to "${ overnight.days }"
        % if overnight.include:
    And I check the checkbox field "childParticipantList[${ loop.index }].onCalculationInd"
        % else:
    And I uncheck the checkbox field "childParticipantList[${ loop.index }].onCalculationInd"
        % endif
      % endfor
    % endif
    And I select "${ number_with_max(parent.additional_minor_children + number_of_non_custodial_children, 5) }" as the field "additionalMinorChildren"
    And I click the button "Continue"
    Then I should see the phrase "Financial Information for: ${ parent.name.full().upper() }"
    % for income_source in parent.income_sources:
    And I select "${ income_source.type }" as the field "incomeRecord[${ loop.index }].incomeTypeCode"
    And I wait 1 second
    And I check the checkbox field "incomeRecord[${ loop.index }].potentialIncome"
      % if income_source.type == 'Employer Wages':
    And I set the field "incomeRecord[${ loop.index }].employer" to "${ income_source.employer_name }"
    And I set the field "incomeRecord[${ loop.index }].grossWageFrequency.sourceAmount" to "${ income_source.gross_income }"
    And I select "${ income_source.frequency }" as the field "incomeRecord[${ loop.index }].grossWageFrequency.frequencyCD"
    And I set the field "incomeRecord[${ loop.index }].overTimeFrequency.sourceAmount" to "${ income_source.overtime }"
    And I select "${ income_source.frequency }" as the field "incomeRecord[${ loop.index }].overTimeFrequency.frequencyCD"
    And I set the field "incomeRecord[${ loop.index }].shiftPremiumFrequency.sourceAmount" to "${ income_source.shift_premium }"
    And I select "${ income_source.frequency }" as the field "incomeRecord[${ loop.index }].shiftPremiumFrequency.frequencyCD"
        % if income_source.must_contribute_to_retirement:
    And I set the field "incomeRecord[${ loop.index }].employeeMandatoryAmt" to "${ income_source.mandatory_percentage }"
        % else:
    And I set the field "incomeRecord[${ loop.index }].employeeMandatoryAmt" to "0"
        % endif
      % else:
        % if income_source.type == 'Self-Employment or 1099':
    And I set the field "incomeRecord[${ loop.index }].employer" to "${ income_source.business_name }"
        % elif income_source.type == "Social Security RSDI, Veterans' Admin, Railroad Retirement, or similar program Dependent Benefits":
          % if income_source.based_on_non_parent:
    And I check the checkbox field "incomeRecord[${ loop.index }].thirdPartyBenefitInd"
          % else:
    And I uncheck the checkbox field "incomeRecord[${ loop.index }].thirdPartyBenefitInd"
          % endif
        % elif income_source.type == "Worker's Compensation Benefits":
    And I set the field "incomeRecord[${ loop.index }].employer" to "${ income_source.employer_name }"
    And I set the field "incomeRecord[${ loop.index }].agencyName" to "${ income_source.agency }"
        % endif
    And I set the field "incomeRecord[${ loop.index }].grossWageFrequency.sourceAmount" to "${ income_source.gross_income }"
    And I select "${ income_source.frequency }" as the field "incomeRecord[${ loop.index }].grossWageFrequency.frequencyCD"
      % endif
      % if not loop.last:
    And I click the button "Add a Source of Income"
    And I wait 1 second
      % endif
    % endfor
    And I set the field "calcDeduction.numIRSExemptions" to "${ parent.tax_exemptions }"
    And I select "${ parent.filing_status }" as the field "calcDeduction.irsFilingStatus"
    And I select "${ parent.city_of_residence }" as the field "calcDeduction.cityOfResidence"
    And I select "${ parent.city_of_employment }" as the field "calcDeduction.cityOfEmployment"
    % if parent.tax_method == 'manual':
    And I select "I know the tax amounts and will enter them" as the id "selectHowToEnterTax"
    And I unfocus
    And I wait 3 seconds
    And I select "${ parent.taxation_frequency }" as the field "calcDeduction.frequency.frequencyCD"
    And I set the field "calcDeduction.fedIncomeTaxOvrdInput" to "${ parent.federal_income_tax }"
    And I set the field "calcDeduction.stateIncomeTaxOvrdInput" to "${ parent.state_income_tax }"
    And I set the field "calcDeduction.ficaTaxOvrdInput" to "${ parent.fica_tax }"
    And I set the field "calcDeduction.resCityTaxOvrdInput" to "${ parent.resident_local_tax }"
    And I set the field "calcDeduction.nonResCityTaxOvrdInput" to "${ parent.non_resident_local_tax }"
    % else:
    And I select "I don't know the tax amounts; estimate monthly taxes for me" as the id "selectHowToEnterTax"
    And I unfocus
    And I wait 3 seconds
    % endif
    % for deduction in parent.deductions:
    And I click the button "Add an Additional Deduction"
    And I wait 1 second
    And I select "${ deduction.type }" as the field "calcAdditionalDeductions[${ loop.index + retirement_index_increment(parent) }].deductionType"
    And I set the field "calcAdditionalDeductions[${ loop.index + retirement_index_increment(parent) }].frequency.sourceAmount" to "${ deduction.amount }"
    And I select "${ deduction.frequency }" as the field "calcAdditionalDeductions[${ loop.index + retirement_index_increment(parent) }].frequency.frequencyCD"
    % endfor
    And I click the button "Continue"
    And I wait 2 seconds
  % endif
    Then I should see the phrase "Child Care Information for: ${ parent.name.full().upper() }"
  % for childcare_expense in parent.childcare_expenses:
    And I click the button "Add a Child Care Expense"
    And I wait 1 second
    % if children.number() == 1 or childcare_expense.all_or_one == 'all':
    And I select "All" as the field "childCareExpenses[${ loop.index }].childId"
    % else:
    And I select "${ childcare_expense.child.name.first.upper() }" as the field "childCareExpenses[${ loop.index }].childId"
    % endif
    And I select "${ childcare_expense.months }" as the field "childCareExpenses[${ loop.index }].numberOfChildCareMonths"
    And I set the field "childCareExpenses[${ loop.index }].guidelineFrequency.sourceAmount" to "${ childcare_expense.amount }"
    And I select "${ childcare_expense.frequency }" as the field "childCareExpenses[${ loop.index }].guidelineFrequency.frequencyCD"
    And I check the checkbox field "childCareExpenses[${ loop.index }].potentialChildCareInd"
  % endfor
  % if parent.override_child_dependent_care_tax_credit:
    And I check the checkbox field "childCareCredits.overrideInd"
    And I set the field "childCareCredits.ccTaxCreditsFrequency.sourceAmount" to "${ parent.child_dependent_care_tax_credit_amount }"
    And I select "${ parent.child_dependent_care_tax_credit_frequency }" as the field "childCareCredits.ccTaxCreditsFrequency.frequencyCD"
  % endif
    And I set the field "childCareCredits.ccSubsidiesFrequency.sourceAmount" to "${ parent.child_care_subsidies_and_reimbursements_amount }"
    And I select "${ parent.child_care_subsidies_and_reimbursements_frequency }" as the field "childCareCredits.ccSubsidiesFrequency.frequencyCD"
  % for child in children:
    % if child.manual_dependency_end_date:
    And I check the checkbox field "childParticipants[${ loop.index }].childCareReimOverrideEndDateInd"
    And I wait 1 second
    And I set the field "childParticipants[${ loop.index }].childCareReimOverrideEndDate" to "${ child.dependency_end_date.format('MM/dd/yyyy') }"
    % endif
  % endfor
    And I click the button "Continue"
    Then I should see the phrase "Medical Information for: ${ parent.name.full().upper() }"
    And I set the field "calcMedIns.medicalInsFreq.sourceAmount" to "${ parent.health_care_insurance_cost }"
    And I select "${ parent.health_care_insurance_frequency }" as the field "calcMedIns.medicalInsFreq.frequencyCD"
  % if parent_code != 'C':
    % if parent.health_insurance_provided_by_other:
    And I select "Yes" as the field "calcMedIns.healthInsProvidedOtherInd"
    % else:
    And I select "No" as the field "calcMedIns.healthInsProvidedOtherInd"
    % endif
  % endif
  % if len(children) == 1:
    % if parent.only_child_covered:
    And I set the field "calcMedIns.childerenOnCalculationCovered" to "1"
    % else:
    And I set the field "calcMedIns.childerenOnCalculationCovered" to "0"
    % endif
  % else:
    And I set the field "calcMedIns.childerenOnCalculationCovered" to "${ len(parent.children_covered) }"
  % endif
    And I set the field "calcMedIns.additionalQualifiedChilderenCovered" to "${ parent.additional_children_covered }"
    And I set the field "calcMedIns.additonalPeopleCovered" to "${ parent.additional_people_covered }"
  % for medical_expense in parent.medical_expenses:
    And I click the button "Add an additional Out-of-Pocket Medical Expense"
    % if children.number() == 1 or medical_expense.all_or_one == 'all':
    And I select "All" as the field "additionalMedicalExpenses[${ loop.index }].childId"
    % else:
    And I select "${ medical_expense.child.name.first.upper() }" as the field "additionalMedicalExpenses[${ loop.index }].childId"
    % endif
    And I set the field "additionalMedicalExpenses[${ loop.index }].addMedicalInsFreq.sourceAmount" to "${ medical_expense.amount }"
    And I select "${ medical_expense.frequency }" as the field "additionalMedicalExpenses[${ loop.index }].addMedicalInsFreq.frequencyCD"
  % endfor
  % if parent_code != 'C':
    % if parent.health_care_coverage_available:
    And I select "Yes" as the field "calcMedIns.reaCostOfHcInd"
    % else:
    And I select "No" as the field "calcMedIns.reaCostOfHcInd"
    And I wait 1 second
      % if parent.reasons_health_care_insurance_not_available['medicaid']:
    And I check the checkbox field "calcMedIns.reaCostHcNoReasons[0].noReasonCd"
      % else:
    And I uncheck the checkbox field "calcMedIns.reaCostHcNoReasons[0].noReasonCd"
      % endif
      % if parent.reasons_health_care_insurance_not_available['six_percent']:
    And I check the checkbox field "calcMedIns.reaCostHcNoReasons[1].noReasonCd"
      % else:
    And I uncheck the checkbox field "calcMedIns.reaCostHcNoReasons[1].noReasonCd"
      % endif
      % if parent.reasons_health_care_insurance_not_available['fifty_percent']:
    And I check the checkbox field "calcMedIns.reaCostHcNoReasons[2].noReasonCd"
      % else:
    And I uncheck the checkbox field "calcMedIns.reaCostHcNoReasons[2].noReasonCd"
      % endif
      % if parent.reasons_health_care_insurance_not_available['poverty']:
    And I check the checkbox field "calcMedIns.reaCostHcNoReasons[3].noReasonCd"
      % else:
    And I uncheck the checkbox field "calcMedIns.reaCostHcNoReasons[3].noReasonCd"
      % endif
    % endif
    % if parent.recommended_to_provide_health_care_insurance:
    And I select "Yes" as the field "recommendedToProvide"
    % else:
    And I select "No" as the field "recommendedToProvide"
    % endif
    % if parent.recommended_to_provide_health_care_insurance:
    And I select "Yes" as the field "calcMedIns.incurMedicalExpenseInd"
    % else:
    And I select "No" as the field "calcMedIns.incurMedicalExpenseInd"
    % endif
  % endif
    And I click the button "Continue"
% endfor
    Then I should see the phrase "Results"
    And I save a screenshot to "output.png"
    And I save the HTML of the page to "output.html"
    And I save the DOM of the page to "dom.html"