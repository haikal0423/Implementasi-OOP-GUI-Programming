import tkinter as tk


class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, dx, dy):
        self.canvas.move(self.item, dx, dy)

    def remove(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 12
        self.velocity = [1, -1]
        # Adjust speed to tweak game difficulty
        self.speed = 6
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#FFFFFF')
        super().__init__(canvas, item)

    def update_position(self):
        coords = self.get_position()
        canvas_width = self.canvas.winfo_width()

        # Reverse direction if hitting walls
        if coords[0] <= 0 or coords[2] >= canvas_width:
            self.velocity[0] *= -1
        if coords[1] <= 0:
            self.velocity[1] *= -1

        dx = self.velocity[0] * self.speed
        dy = self.velocity[1] * self.speed
        self.move(dx, dy)

    def check_collision(self, objects):
        coords = self.get_position()
        ball_center_x = (coords[0] + coords[2]) * 0.5

        if len(objects) > 1:
            self.velocity[1] *= -1
        elif len(objects) == 1:
            obj = objects[0]
            obj_coords = obj.get_position()
            if ball_center_x > obj_coords[2]:
                self.velocity[0] = 1
            elif ball_center_x < obj_coords[0]:
                self.velocity[0] = -1
            else:
                self.velocity[1] *= -1

        for obj in objects:
            if isinstance(obj, Brick):
                obj.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 15
        self.attached_ball = None
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill='#FFA500')
        super().__init__(canvas, item)

    def attach_ball(self, ball):
        self.attached_ball = ball

    def move(self, offset):
        coords = self.get_position()
        canvas_width = self.canvas.winfo_width()
        if 0 <= coords[0] + offset and coords[2] + offset <= canvas_width:
            super().move(offset, 0)
            if self.attached_ball:
                self.attached_ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#FF4500', 2: '#32CD32', 3: '#1E90FF'}

    def __init__(self, canvas, x, y, health):
        self.width = 70
        self.height = 25
        self.health = health
        color = Brick.COLORS[health]
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=color, tags='brick')
        super().__init__(canvas, item)

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.remove()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.health])


class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.lives = 3
        self.width = 600
        self.height = 450
        self.canvas = tk.Canvas(self, bg='#ADD8E6', width=self.width, height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 350)
        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 70):
            self.add_brick(x + 35, 50, 3)
            self.add_brick(x + 35, 80, 2)
            self.add_brick(x + 35, 110, 1)

        self.status_text = None
        self.initialize_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-20))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(20))

    def initialize_game(self):
        self.add_ball()
        self.update_lives_display()
        self.status_text = self.display_message(self.width / 2, self.height / 2, 'Press Space to Start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball:
            self.ball.remove()
        paddle_coords = self.paddle.get_position()
        ball_x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, ball_x, 340)
        self.paddle.attach_ball(self.ball)

    def add_brick(self, x, y, health):
        brick = Brick(self.canvas, x, y, health)
        self.items[brick.item] = brick

    def display_message(self, x, y, text, font_size=30):
        font = ('Arial', font_size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_display(self):
        lives_text = f'Lives: {self.lives}'
        if not self.status_text:
            self.status_text = self.display_message(50, 20, lives_text, 16)
        else:
            self.canvas.itemconfig(self.status_text, text=lives_text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.status_text)
        self.paddle.attached_ball = None
        self.run_game_loop()

    def run_game_loop(self):
        self.check_collisions()
        remaining_bricks = len(self.canvas.find_withtag('brick'))

        if remaining_bricks == 0:
            self.ball.speed = 0
            self.display_message(self.width / 2, self.height / 2, 'You Win!')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = 0
            self.lives -= 1
            if self.lives < 0:
                self.display_message(self.width / 2, self.height / 2, 'Game Over!')
            else:
                self.after(1000, self.initialize_game)
        else:
            self.ball.update_position()
            self.after(40, self.run_game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        overlapping_items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[obj] for obj in overlapping_items if obj in self.items]
        self.ball.check_collision(objects)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker Game')
    game = Game(root)
    game.mainloop()
