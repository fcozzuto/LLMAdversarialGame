def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    pursuer = ("pursuer" in roles) and ("evader" not in roles)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    ti = int(observation.get("turn_index", 0))
    # Deterministic corner choice: rotate among corners to reduce predictability.
    if not corners:
        target = (w - 1, h - 1)
    else:
        target = corners[ti % 4]
        best_corner_val = -10**9
        for c in corners:
            v = man(c[0], c[1], ox, oy)
            if v > best_corner_val:
                best_corner_val = v
                target = c

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        if pursuer:
            # Chase directly, but lightly prefer diagonal when distances tie.
            score = -d * 1000 - (abs(dx) + abs(dy)) * 0.5
        else:
            # Evade: maximize distance, while steering toward farthest corner (selected deterministically).
            score = d * 1000 - man(nx, ny, target[0], target[1]) * 25 - (abs(dx) + abs(dy)) * 0.01

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best