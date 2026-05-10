def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal_pos(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def clearance(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if legal_pos(nx, ny):
                c += 1
        return c

    pursuer = ("pursuer" in self_role) or ("pursuit" in self_role) or ("evader" not in self_role)
    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal_pos(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        c = clearance(nx, ny)
        # pursuer: minimize distance; evader: maximize distance
        score = (-d if pursuer else d) + 0.05 * c
        key = (score, -nx, -ny) if pursuer else (score, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move