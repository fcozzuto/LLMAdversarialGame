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

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
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

    tr = int(observation.get("turns_remaining", 0))
    prefer_feasible = (tr % 3 != 0)

    best = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        feasible = (my_d <= op_d)
        # tuple sorts lexicographically ascending, so negate where larger is better
        score = (0 if (prefer_feasible and feasible) else 1,
                 -(op_d - my_d),
                 my_d,
                 rx,
                 ry)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = sx + dx
            ny = sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d_to_target = cheb(nx, ny, tx, ty)
            d_to_opp = cheb(nx, ny, ox, oy)
            # Prefer getting closer; if tied, prefer making opponent farther; deterministic by nx,ny
            cand = (d_to_target, -(d_to_opp - cheb(ox, oy, tx, ty)), nx, ny, dx, dy)
            candidates.append(cand)

    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][4]), int(candidates[0][5])]