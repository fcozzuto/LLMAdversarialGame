def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Pick best target: maximize how much earlier we can arrive than opponent.
    best = None
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Slightly favor resources that are closer to us when ties happen.
        key = (opd - myd, -myd, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # One-step deterministic evaluation to avoid stepping into obstacles.
    best_mv = (0, 0)
    best_mv_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; if both similar, keep improving the lead.
        key = (-d_to_target, (d_opp - d_to_target), -dx, -dy, nx, ny)
        if best_mv_key is None or key > best_mv_key:
            best_mv_key = key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]