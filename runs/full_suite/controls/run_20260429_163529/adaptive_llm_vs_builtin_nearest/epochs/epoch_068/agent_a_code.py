def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource by race advantage: (opponent distance) - (self distance)
    # Tie-break deterministically by preferring closer to our side toward opponent corner.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Favor resources that are "ahead" toward opponent: increase with coordinate toward opponent
        # Opponent corner may be (7,7) typically; generalize by using cheb to a "directional" dot.
        dir_score = (rx - (w - 1 - rx)) + (ry - (h - 1 - ry))
        key = (od - sd, sd, -dir_score, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose best move among legal deltas by minimizing distance to target, with obstacle avoidance.
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best_m = None
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # primary: closer to target; secondary: avoid giving opponent immediate advantage
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # small deterministic bias to keep motion stable
        bias = (dx, dy)
        k = (-d_to, d_to, d_opp, bias[0], bias[1])
        if best_k is None or k > best_k:
            best_k = k
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]