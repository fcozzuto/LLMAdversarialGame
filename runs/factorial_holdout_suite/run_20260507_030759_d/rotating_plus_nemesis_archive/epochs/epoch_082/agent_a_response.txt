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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
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

    if (sx, sy) in resources:
        return [0, 0]

    # Pick target that maximizes "lead" (opponent slower than us), then minimizes our distance.
    best_t = None
    best_score = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead = od - sd
        score = (lead, -sd)  # lexicographic: prefer larger lead, then smaller sd
        if best_score is None or score > best_score:
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = None
    best_m_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Prefer moves that keep/improve lead vs opponent (opponent position assumed static this turn).
        lead = nod - nsd
        # Small bias: don't drift away from a close target.
        key = (lead, -nsd, -abs(nx - tx) - abs(ny - ty))
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = [dx, dy]

    if best_m is None:
        return [0, 0]
    return best_m