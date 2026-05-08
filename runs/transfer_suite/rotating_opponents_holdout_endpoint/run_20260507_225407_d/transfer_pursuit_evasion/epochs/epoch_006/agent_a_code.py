def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None:
            continue
        obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("catch" in role) or ("purs" in opp_role) or ("catch" in opp_role) or ("evad" in role and "evad" not in opp_role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, target[0], target[1])
        score = 0.0
        if is_pursuer:
            score = -d_opp - 0.02 * d_corner
        else:
            score = d_opp - 0.02 * d_corner
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move