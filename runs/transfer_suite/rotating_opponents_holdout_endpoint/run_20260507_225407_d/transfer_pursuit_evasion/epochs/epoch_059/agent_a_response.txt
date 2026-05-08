def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("evasion" in r) or ("avoid" in r)

    self_is_evader = is_evader(observation.get("self_role", "")) or is_evader(observation.get("self_role_name", ""))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    adj = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def obs_pressure(x, y):
        # Penalize getting boxed in / near obstacles
        c_free = 0
        near = 0
        for dx, dy in adj:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                if (nx, ny) not in obstacles:
                    c_free += 1
                else:
                    near += 1
        return -near, c_free

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        p1, c_free = obs_pressure(nx, ny)
        e = edge_dist(nx, ny)

        # If evader: maximize distance, avoid obstacles, avoid edge trapping (stay with larger edge distance)
        # If pursuer: minimize distance, avoid obstacles, move toward tighter chase positioning (slightly prefer lower edge distance)
        if self_is_evader:
            score = 2.2 * d + 0.7 * c_free + 0.35 * e + 1.0 * p1
        else:
            score = -2.2 * d + 0.9 * c_free - 0.25 * e + 1.0 * p1

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]