def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Prefer resources we can reach no later than opponent; tie-break by smallest our distance then position.
    best = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        tx = int(r[0]); ty = int(r[1])
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obstacles:
            continue
        my_d = cheb(sx, sy, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        lead = my_d - op_d  # <=0 means we are earlier or tie
        # Deterministic score: prioritize lead<=0, then smaller my_d, then lexicographic target
        if lead <= 0:
            score = (0, my_d, tx, ty)
        else:
            # If no non-losing option exists, keep options that minimize how far behind we are
            score = (1, lead, my_d, tx, ty)
        if best is None or score < best[0]:
            best = (score, tx, ty)

    tx, ty = best[1], best[2]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try one-axis move deterministically
        if dx != 0 and (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if dy != 0 and (sx, sy + dy) not in obstacles:
            return [0, dy]
        return [0, 0]
    return [dx, dy]