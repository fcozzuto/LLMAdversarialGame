def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "")
    pursuer = ("pursuer" in role.lower()) or ("catch" in role.lower()) or ("hunter" in role.lower())

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def cornered(x, y):
        return (x == 0 or x == w - 1) + (y == 0 or y == h - 1)

    def open_degree(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    def block_to_corner(nx, ny):
        # Encourage moving so that opponent's next corner direction is constrained.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        step_x = 0 if tx == ox else (1 if tx > ox else -1)
        step_y = 0 if ty == oy else (1 if ty > oy else -1)
        ax, ay = ox + step_x, oy + step_y
        if not inb(ax, ay):
            return 0.0
        # If we can occupy the cell that "follows" the opponent toward its corner, it's blocking.
        return 1.0 if (nx == ax and ny == ay) else 0.0

    opp_corner = cornered(ox, oy)

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = dist2(nx, ny)
        deg = open_degree(nx, ny)

        # Heuristic: minimize distance (pursuer) / maximize distance (evader).
        # Also, if opponent is cornered, prioritize "blocking" move and reduce available escape.
        escape_pressure = -deg
        block = block_to_corner(nx, ny) * (1.0 + 0.6 * opp_corner)

        score = (-d) if not pursuer else (-d)  # convert to common minimization later
        # For pursuer: want smaller d, larger deg reduction/blocks.
        if pursuer:
            score = d - 0.25 * deg - 1.2 * block
        else:
            score = -d + 0.25 * deg + 0.8 * block

        if best_score is None or (score < best_score if pursuer else score < best_score):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]