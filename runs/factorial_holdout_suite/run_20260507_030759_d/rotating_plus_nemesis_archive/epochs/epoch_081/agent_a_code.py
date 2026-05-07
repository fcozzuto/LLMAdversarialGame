def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # If standing on a resource (shouldn't happen often), don't waste a move.
    if (sx, sy) in res_set:
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead = od - sd
        key = (lead, -sd, (tx + ty) & 1, -ty, -tx)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    candidates = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Deterministic preference: maximize resource pickup, then move to reduce our distance, while keeping lead.
    best_move = [0, 0]
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        self_dist_next = cheb(nx, ny, tx, ty)
        opp_dist_next = cheb(ox, oy, tx, ty)
        lead_next = opp_dist_next - self_dist_next
        pick = 1 if (nx, ny) in res_set else 0
        score = (pick * 10**6) + (lead_next * 10**3) - self_dist_next - (dx*dx + dy*dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]