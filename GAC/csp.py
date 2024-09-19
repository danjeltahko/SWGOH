"""
# Constraint Satisfaction Problems

Finding a solution that meets a set of consstraints is the goal of
constraint satisfaction problems (CSPs). Finding values for a group
of variables that fulfill a set of restrictions or rules is the aim
of constraint satisfaction problems.

There are mainly three components in a CSP:

### Variables:
    The unknowns that need to be assigned a value. For example, in
    a GAC problem, the variables are the defense teams.

### Domains:
    The set of values that can be assigned to a variable. For example,
    in a GAC problem, the domains are the attack teams that can be
    assigned to a defense team.

### Constraints:
    The restrictions that limit the values that can be assigned to
    variables. For example, in a GAC problem, the constraints are that
    no attack team should be used more than once and that the attack
    team should not have any characters that are already used.

"""

from printinglog import Logger
import copy

logger = Logger(format="simple")


class CSP:
    """
    A class to represent a Constraint Satisfaction Problem (CSP).

    Attributes
    ----------
    variables : list[int]
        A list of variable indices.
    domains : list[tuple[int, dict]]
        A list of tuples with the variable index and the domain values.
    constraints : function
        A function that checks if the assignment is consistent.
    logging : bool
        A optional boolean to enable logging.
    solution : list
        The best solution found.
    max_total_win_rate : int
        The maximum total win rate found.
    iteration : int
        The number of iterations.

    """

    def __init__(
        self,
        variables: list[int],
        domains: list[tuple[int, dict]],
        logging: bool = False,
    ):
        """
        Constructs all the necessary attributes for the CSP object.

        Parameters
        ----------
        variables : list[int]
            A list of variable indices.
        domains : list[tuple[int, dict]]
            A list of tuples with the variable index and the domain values.
        logging : bool, optional
            A boolean to enable logging, by default False.
        """
        self.variables = variables
        self.domains = domains
        self.logging = logging
        self.solution = None
        self.max_total_win_rate = -1
        self.iteration = 0

    def solve(self):
        """
        Solves the CSP problem.
        """
        assignment = []
        self.backtrack(assignment)
        return self.solution

    def backtrack(self, assignment: list):
        """
        Backtracking algorithm to solve the CSP problem.

        Parameters
        ----------
        assignment : list
            A list of tuples with the variable index and the domain values.
        """
        # If the assignment is complete, check if it is the best solution
        if len(assignment) == len(self.variables):
            # Calculate the total win rate for the assignment
            total_win_rate = sum(
                counter["best_team"]["win_rate"] for _, counter in assignment
            )
            # Save the best solution, which will be returned when done
            if total_win_rate > self.max_total_win_rate:
                self.max_total_win_rate = total_win_rate
                self.solution = copy.deepcopy(assignment)

            return

        # Calculate the potential maximum total win rate from this point
        potential_total = sum(
            counter["best_team"]["win_rate"] for _, counter in assignment
        )
        # Calculate the maximum win rate for the remaining variables
        remaining_win_rates = [
            max(
                [
                    counter["win_rate"]
                    for counter in self.order_domain(index=var)["counters"]
                ]
                or [0]
            )
            for var in self.variables
            if var not in [a[0] for a in assignment]
        ]
        potential_total += sum(remaining_win_rates)
        if potential_total <= self.max_total_win_rate:
            # Prune this path as it cannot improve the best solution
            return

        # Get the first variable index that is not in the assignment
        var = self.select_unassigned_variable(assignment)
        assigned = False
        # Iterate over the domain values for the variable
        for value in self.order_domain_values(var):
            """
            value:
            {
                "attack": [
                    {
                        "name": name,
                        "base_id": base_id,
                        "categories": categories
                        "image": image
                    }
                ],
                "win_rate": 100,
                "has_gl": True
            }
            """
            # value = {"attack" & "win_rate"}

            # Check if the value is consistent with the assignment
            if self.is_consistent(var, value, assignment):
                # Order the domain values for the variable index
                domain = self.order_domain(var)
                # Add the best team to the domain
                domain["best_team"] = value
                # Add the variable and domain to the assignment
                assignment.append((var, domain))

                # Log the assignment
                if self.logging:
                    print("\n=================================================")
                    logger.info(f"ITERATION {self.iteration}\n")
                    for i, counter in assignment:
                        print(f"({i}) Defense: {counter['defense']}")
                        print(
                            f"Best counter ({counter['best_team']['win_rate']}): {counter['best_team']['attack']}\n"
                        )
                    print("\n---------------------------------------------\n")
                    self.iteration += 1

                # Recursively call backtrack
                assigned = True
                self.backtrack(assignment)
                assignment.pop()

        # If no value was assigned, add the variable without a value
        if not assigned:
            domain = self.order_domain(var)
            domain["best_team"] = {"attack": [], "win_rate": 0}
            assignment.append((var, domain))
            self.backtrack(assignment)
            assignment.pop()

    def select_unassigned_variable(self, assignment: list):
        """
        Selects the variable with the smallest domain size.

        Parameters
        ----------
        assignment : list
            A list of tuples with the variable index and the domain values.

        Returns
        -------
        int
            The variable index with the smallest domain size.
        """

        # MRV: Minimum Remaining Values
        unassigned_variables = [
            var for var in self.variables if var not in [a[0] for a in assignment]
        ]
        # Calculate the domain size for each variable
        var_domain_size = []
        for var in unassigned_variables:
            legal_values = [value for value in self.order_domain_values(var)]
            var_domain_size.append((var, len(legal_values)))
        # Select the variable with the smallest domain size
        var_domain_size.sort(key=lambda x: x[1])
        return var_domain_size[0][0] if var_domain_size else None

    def order_domain(self, index: int) -> dict:
        """
        Returns:
        {
            "defense": [
                {
                    "name": name,
                    "base_id": base_id,
                    "categories": categories
                    "image": image
                }
            ],
            "counters": [
                {
                    "attack": [
                        {
                            "name": name,
                            "base_id": base_id,
                            "categories": categories
                            "image": image
                        }
                    ],
                    "win_rate": 100,
                    "has_gl": True
                }
            ],
            "best_team": {
                "attack": [
                    {
                        "name": name,
                        "base_id": base_id,
                        "categories": categories
                        "image": image
                    }
                ],
                "win_rate": 100
            }
        }

        """
        domain = [d for i, d in self.domains if i == index]
        return domain[0]

    def order_domain_values(self, var) -> list[dict]:
        """
        Returns:
        {
            "attack": [
                {
                    "name": name,
                    "base_id": base_id,
                    "categories": categories
                    "image": image
                }
            ],
            "win_rate": 100,
            "has_gl": True
        }
        """
        domain = self.order_domain(index=var)
        # Order the domains values for the variable index
        # domain_value = [counter for counter in domain["counters"]]
        domain_value = sorted(
            domain["counters"], key=lambda x: x["win_rate"], reverse=True
        )
        return domain_value

    def is_consistent(self, var: int, value: dict, assignment: list) -> bool:
        """
        Check if the value is consistent with the assignment.

        Parameters
        ----------
        var : int
            The index of the variable.
        value : dict
            The domain value for the index team.
        assignment : list
            A list with all the values with their index.

        Returns
        -------
        bool
            True if the value is consistent with the assignment, otherwise False.
        """

        """
        index = Index of the variable
        var = {
            "attack": [
                {
                    "name": name,
                    "base_id": base_id,
                    "categories": categories
                    "image": image
                }
            ],
            "win_rate": 100,
            "has_gl": True
        }
        assignment = [(index, dict={

                "defense": [CHARACTER1, ...],
                "counters": [
                    {
                        "attack": [CHARACTER1, ...],
                        "win_rate": 100
                    },..
                ],
                "best_team": {
                    "attack": [CHARACTER1, ...],
                    "win_rate": 100
                }
            })]
        """

        # 1. Return True if nothing to compare with
        if not assignment:
            return True

        # 2. Compare if unit exists in any other team
        for unit in value["attack"]:
            for _, team in assignment:
                # Same Unit exists in other assigned team
                if unit["base_id"] in [
                    character["base_id"] for character in team["best_team"]["attack"]
                ]:
                    return False

        # 3. If defense team has a GL, then win rate
        # threshold should be 80% or more...
        if value["has_gl"] and value["win_rate"] < 80:
            return False

        return True


def calculate(data: dict):

    print("==== CALCULATING BEST ATTACK ====\n")

    # Creation of variables with index for each def team
    variables = []
    index = 0
    for zone in data:
        for _ in data[zone]:
            variables.append(index)
            index += 1

    logger.info(f"Variables Creation - Defense teams: {variables}")

    # Creation of domain with index for each (variable-team)
    domain = [
        (i, var) for i, var in enumerate([team for zone in data for team in data[zone]])
    ]
    logger.info(f"Domains Created")

    csp = CSP(variables=variables, domains=domain, logging=False)
    sol = csp.solve()

    return sol
