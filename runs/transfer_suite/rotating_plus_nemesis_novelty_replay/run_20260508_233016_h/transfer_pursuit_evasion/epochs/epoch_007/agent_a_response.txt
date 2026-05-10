def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" in opp_role and "evad" not in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y):
        return abs(x - ox) + abs(y - oy)

    def wall_pen(x, y):
        # encourage/avoid sticking to walls depending on role
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            d = dist(nx, ny)
            if pursuer:
                # prefer getting closer; slight push toward center to reduce being cornered
                score = d * 100 - wall_pen(nx, ny) * 3
            else:
                # evade: prefer getting farther; also avoid edges a bit (more mobility)
                score = (-d) * 100 + wall_pen(nx, ny) * 3
            moves.append((score, dx, dy))

    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (t[0], t[1], t[2]))
    _, dx, dy = moves[0]
    return [int(dx), int(dy)]