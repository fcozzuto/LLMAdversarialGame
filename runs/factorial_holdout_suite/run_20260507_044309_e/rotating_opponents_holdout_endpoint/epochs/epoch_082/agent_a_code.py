def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    best = None
    best_key = None
    ti = int(observation.get("turn_index", 0) or 0)
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer clear lead, then shorter for us, then stable tie-break; small parity term to vary targets deterministically.
        key = ((od - sd) * 1000 + (-sd) * 10 + (-(rx * 100 + ry)) + (ti % 2))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
                continue
            dist = cheb(nx, ny, tx, ty)
            # Also penalize moving closer for opponent to the same target.
            od = cheb(ox, oy, tx, ty)
            o_after = cheb(ox, oy, tx, ty)  # opponent position doesn't change; keep simple/deterministic.
            parity = ((nx + ny + ti) % 3) - 1
            key = (-dist, (dist == cheb(sx, sy, tx, ty)), -(o_after), parity, -(dx * dx + dy * dy))
            moves.append((key, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True, key=lambda t: t[0])
    _, dx, dy = moves[0]
    return [int(dx), int(dy)]