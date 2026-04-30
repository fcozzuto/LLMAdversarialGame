def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, retreat toward center to avoid edges.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dx = 1 if sx < cx else (-1 if sx > cx else 0)
        dy = 1 if sy < cy else (-1 if sy > cy else 0)
        return [dx, dy]

    # Pick a resource where we have advantage; otherwise minimize our distance.
    best = None
    best_val = -10**9
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        adv = od - sd  # positive means we are closer/equal
        # Small tie-break toward resources closer to our diagonal (avoid flipping too much).
        diag_pref = -((sx - x) * (sy - y))
        val = adv * 100 - sd * 3 + diag_pref
        if val > best_val:
            best_val = val
            best = (x, y)

    tx, ty = best

    # Choose best step among legal deltas that reduces distance; avoid obstacles.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    curd = cheb(sx, sy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            nd = cheb(nx, ny, tx, ty)
            # Prefer strict improvement; if equal, prefer avoiding being closer than opponent would be.
            od_now = cheb(ox, oy, tx, ty)
            od_after = cheb(ox + (1 if ox < tx else (-1 if ox > tx else 0)), oy + (1 if oy < ty else (-1 if oy > ty else 0)), tx, ty) if False else od_now
            candidates.append((nd, - (od_now - nd), 0 if dx == 0 and dy == 0 else 1, dx, dy))
    # Deterministic selection: minimize nd, then maximize advantage (- (od_now - nd)), then prefer moving over staying.
    candidates.sort()
    _, _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]