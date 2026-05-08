def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None:
            continue
        obstacles.add((int(p[0]), int(p[1])))

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
    is_pursuer = ("purs" in role) or ("catch" in role) or ("purs" in opp_role) or ("catch" in opp_role)

    dirs = [(-1, -1), (1, 1), (-1, 1), (1, -1), (-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_score = None
    best_move = [0, 0]

    # Secondary preference: keep toward center for evader, toward opponent for pursuer
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dist = cheb(nx, ny, ox, oy)
        if is_pursuer:
            # minimize distance; break ties by preferring "toward opponent direction" and away from center is not needed
            score = (-dist, -((nx - ox) ** 2 + (ny - oy) ** 2), abs(nx - cx) + abs(ny - cy))
        else:
            # maximize distance; tie-break by going toward corners away from opponent and away from center if possible
            score = (dist, (nx - cx) ** 2 + (ny - cy) ** 2, (nx + ny) - (ox + oy))

        if best_score is None or (score > best_score if not is_pursuer else score > best_score):
            best_score = score
            best_move = [dx, dy]

    # If all moves invalid (shouldn't happen), stay
    return best_move