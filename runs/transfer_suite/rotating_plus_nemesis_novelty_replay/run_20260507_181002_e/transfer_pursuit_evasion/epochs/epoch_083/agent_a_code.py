def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "") or "")
    i_am_evader = ("evad" in role.lower())

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def obstacle_density(x, y):
        c = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (x + ex, y + ey) in obstacles:
                    c += 1
        return c

    def wall_pen(x, y):
        d = min(x, y, w - 1 - x, h - 1 - y)
        return (0 if d >= 2 else (-0.25 if d == 1 else -0.7))

    # Deterministic tie-break order: fixed moves list and score comparison only.
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d2 = dist(nx, ny, ox, oy)
        # If pursuer: minimize distance; if evader: maximize distance.
        # Strong preference for immediate capture (distance 0).
        capture_bonus = 0.0
        if d2 == 0:
            capture_bonus = 10000.0

        # Also bias away from crowded obstacle regions; slight wall bias.
        dens = obstacle_density(nx, ny)
        wp = wall_pen(nx, ny)

        if i_am_evader:
            val = (-d2) + 3.2 * capture_bonus + 0.35 * dens + 0.25 * wp
        else:
            val = (-d2) + 3.2 * capture_bonus - 0.45 * dens + 0.25 * wp

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move