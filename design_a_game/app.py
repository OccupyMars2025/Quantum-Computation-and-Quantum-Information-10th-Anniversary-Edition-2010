
import json

class User:
    def __init__(self, name, points=0, badges=None):
        if badges is None:
            badges = []
        self.name = name
        self.points = points
        self.badges = badges

    def complete_challenge(self, challenge_name, points):
        self.points += points
        print(f"{self.name} completed '{challenge_name}' and earned {points} points! Total points: {self.points}")

    def earn_badge(self, badge_name):
        self.badges.append(badge_name)
        print(f"{self.name} earned a badge: '{badge_name}'! Total badges: {len(self.badges)}")

    def display_status(self):
        print(f"User: {self.name}\nPoints: {self.points}\nBadges: {', '.join(self.badges)}\n")

    def to_dict(self):
        return {"name": self.name, "points": self.points, "badges": self.badges}

    @classmethod
    def from_dict(cls, data):
        return cls(data['name'], data['points'], data['badges'])    
        

class PointsAndBadgesSystem:
    def __init__(self, data_file='user_data.json'):
        self.users = {}
        self.leaderboard = {}
        self.data_file = data_file
        self.load_data()

    def register_user(self, name):
        if name not in self.users:
            self.users[name] = User(name)
            print(f"User '{name}' registered successfully.")
            self.save_data()
        else:
            print(f"User '{name}' already exists.")

    def complete_challenge(self, name, challenge_name, points):
        if name in self.users:
            self.users[name].complete_challenge(challenge_name, points)
            self.update_leaderboard(name)
            self.save_data()
        else:
            print(f"User '{name}' not found.")

    def earn_badge(self, name, badge_name):
        if name in self.users:
            self.users[name].earn_badge(badge_name)
            self.save_data()
        else:
            print(f"User '{name}' not found.")

    def update_leaderboard(self, name):
        user = self.users[name]
        self.leaderboard[name] = user.points

    def display_leaderboard(self):
        sorted_leaderboard = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
        print("\nLeaderboard:")
        for i, (user, points) in enumerate(sorted_leaderboard, 1):
            print(f"{i}. {user}: {points} points")

    def display_user_status(self, name):
        if name in self.users:
            self.users[name].display_status()
        else:
            print(f"User '{name}' not found.")

    def save_data(self):
        with open(self.data_file, 'w') as file:
            json.dump({name: user.to_dict() for name, user in self.users.items()}, file)

    def load_data(self):
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                self.users = {name: User.from_dict(user_data) for name, user_data in data.items()}
                self.leaderboard = {name: user.points for name, user in self.users.items()}
        except FileNotFoundError:
            pass          


from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
system = PointsAndBadgesSystem()

@app.route('/')
def index():
    html = '''
    <h1>Welcome to the Quantum Quest Points and Badges System!</h1>
    <h2>Available Actions:</h2>
    <ul>
        <li><a href="/register">Register a User</a></li>
        <li><a href="/complete_challenge">Complete a Challenge</a></li>
        <li><a href="/earn_badge">Earn a Badge</a></li>
        <li><a href="/leaderboard">View Leaderboard</a></li>
        <li><a href="/user_status">View User Status</a></li>
    </ul>
    '''
    return render_template_string(html)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        system.register_user(name)
        return jsonify({"message": f"User '{name}' registered successfully."})
    return '''
        <h2>Register a User</h2>
        <form method="post">
            Name: <input type="text" name="name"><br>
            <input type="submit" value="Register">
        </form>
    '''

@app.route('/complete_challenge', methods=['GET', 'POST'])
def complete_challenge():
    if request.method == 'POST':
        name = request.form['name']
        challenge_name = request.form['challenge_name']
        points = int(request.form['points'])
        system.complete_challenge(name, challenge_name, points)
        return jsonify({"message": f"User '{name}' completed '{challenge_name}' and earned {points} points."})
    return '''
        <h2>Complete a Challenge</h2>
        <form method="post">
            Name: <input type="text" name="name"><br>
            Challenge Name: <input type="text" name="challenge_name"><br>
            Points: <input type="number" name="points"><br>
            <input type="submit" value="Complete Challenge">
        </form>
    '''

@app.route('/earn_badge', methods=['GET', 'POST'])
def earn_badge():
    if request.method == 'POST':
        name = request.form['name']
        badge_name = request.form['badge_name']
        system.earn_badge(name, badge_name)
        return jsonify({"message": f"User '{name}' earned a badge: '{badge_name}'."})
    return '''
        <h2>Earn a Badge</h2>
        <form method="post">
            Name: <input type="text" name="name"><br>
            Badge Name: <input type="text" name="badge_name"><br>
            <input type="submit" value="Earn Badge">
        </form>
    '''

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    sorted_leaderboard = sorted(system.leaderboard.items(), key=lambda x: x[1], reverse=True)
    return jsonify(sorted_leaderboard)

@app.route('/user_status', methods=['GET', 'POST'])
def user_status():
    if request.method == 'POST':
        name = request.form['name']
        if name in system.users:
            user = system.users[name]
            return jsonify({"name": user.name, "points": user.points, "badges": user.badges})
        else:
            return jsonify({"message": f"User '{name}' not found."})
    return '''
        <h2>View User Status</h2>
        <form method="post">
            Name: <input type="text" name="name"><br>
            <input type="submit" value="View Status">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)