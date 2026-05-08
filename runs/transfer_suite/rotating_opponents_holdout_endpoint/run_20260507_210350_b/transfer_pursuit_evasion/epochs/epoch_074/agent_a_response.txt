def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    role_opp = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = any(k in role_self for k in ("pursuer", "chaser", "hunter"))
    opp_is_pursuer = any(k in role_opp for k in ("pursuer", "chaser", "hunter"))
    i_am_pursuer = self_is_pursuer if (self_is_pursuer or opp_is_pursuer) else True

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer staying closer (pursuer) / farther (evader), avoid obstacles, and corner/edge bias.
    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        # edge/corner bias via Manhattan distance to nearest edge (lower is more cornered)
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)
        # wall avoidance: slightly penalize moves that step "behind" obstacle in direction of opponent
        obs_pen = 0
        for (bx, by) in obstacles:
            if bx == nx or by == ny:
                obs_pen += 1
        # If pursuer, minimize distance; if evader, maximize distance.
        sign = 1 if i_am_pursuer else -1
        # Deterministic tie-break: smaller resulting dx,dy lexicographic toward reducing x then y.
        score = sign * d + (0.02 if i_am_pursuer else -0.02) * edge + 0.1 * obs_pen
        tie = (abs(dx), abs(dy), 0 if dx == 0 else (0 if dx < 0 else 1), 0 if dy == 0 else (0 if dy < 0 else 1))
        key = (score, tie)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    # If all moves blocked, stay.
    return best_move