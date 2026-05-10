def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        obs.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evad" in self_role) or ("evader" in self_role) or ("escape" in self_role)
    self_is_pursuer = ("purs" in self_role) or ("capt" in self_role) or ("chase" in self_role)
    if ("evad" in opp_role) or ("evader" in opp_role) or ("escape" in opp_role):
        self_is_evader = False
    if ("purs" in opp_role) or ("capt" in opp_role) or ("chase" in opp_role):
        self_is_pursuer = False
    mode = "evade" if self_is_evader and not self_is_pursuer else "pursue"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    def mdist(x, y):
        dx = x - ox
        if dx < 0:
            dx = -dx
        dy = y - oy
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = mdist(nx, ny)
        val = d if mode == "evade" else -d
        if best is None or val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]