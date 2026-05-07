def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    if (sx, sy) in resources:
        return [0, 0]

    def cheby(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Choose resource where we arrive earlier than opponent; prefer maximal lead, then closest.
    best = None
    for tx, ty in resources:
        if (tx, ty) == (sx, sy):
            return [0, 0]
        ds = cheby(sx, sy, tx, ty)
        do = cheby(ox, oy, tx, ty)
        lead = do - ds  # positive means we are closer/equal earlier
        # If opponent is closer, slightly penalize even if we are closer in raw distance.
        score = (lead * 1000) - (ds * 7) + (1 if lead >= 0 else -1)
        if best is None or score > best[0] or (score == best[0] and ds < best[1]):
            best = (score, ds, tx, ty)

    _, _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Deterministic fallback: try axis moves toward target.
        cand = []
        if dx != 0 and (sx + dx, sy) not in obstacles:
            cand.append((dx, 0))
        if dy != 0 and (sx, sy + dy) not in obstacles:
            cand.append((0, dy))
        if dx != 0 and dy != 0 and (sx + dx, sy) in obstacles and (sx, sy + dy) in obstacles:
            cand = [(0, 0)]
        if cand:
            return [int(cand[0][0]), int(cand[0][1])]
        return [0, 0]

    return [int(dx), int(dy)]