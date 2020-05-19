class User:
    """docstring for User"""

    def __init__(self, name, email, batch, profile_url, cf_id, cc_id):
        self.name = name
        self.email = email
        self.profile_url = profile_url
        self.cf_id = cf_id
        self.cc_id = cc_id
        self.batch = batch
        self.cf_url = "https://codeforces.com/profile/" + cf_id
        self.cc_url = "https://www.codechef.com/users/" + cc_id
        self.cf_sol = 0
        self.cc_sol = 0
        self.total_sol = 0

    def get_total_sol(self):
        self.total_sol = self.cf_sol + self.cc_sol
        return self.total_sol
