def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role_s = str(observation.get("self_role", "")).lower()
    i_am_pursuer = any(k in role_s for k in ("pursuer", "chaser", "catch", "pursuit"))

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    cap_r = int(observation.get("capture_radius", 0) or 0)

    def cheb(x, y, tx, ty):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def obstacle_adjacency(x, y):
        s = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in blocked:
                    s += 1
        return s

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]

    # Deterministic target corner for evader: maximize distance from pursuer.
    corner_targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = corner_targets[0]
    best_corner_d = -1
    for cx, cy in corner_targets:
        d = cheb(cx, cy, ox, oy)
        if d > best_corner_d:
            best_corner_d = d
            best_corner = (cx, cy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_to_opp = cheb(nx, ny, ox, oy)
        adj = obstacle_adjacency(nx, ny)

        if i_am_pursuer:
            # Pursuer: prioritize capture, otherwise minimize distance; avoid tight obstacle adjacency.
            if d_to_opp <= cap_r:
                score = -10_000 - adj
            else:
                score = d_to_opp * 100 + adj
            # lower is better
            if best_move == [0, 0] or score < best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            # Evader: prioritize increasing distance from pursuer; also head for farthest corner.
            d_corner = cheb(nx, ny, best_corner[0], best_corner[1])
            # higher is better; discourage obstacle adjacency but keep it secondary
            score = d_to_opp * 100 + d_corner * 10 - adj * 2
            if best_move == [0, 0] or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]