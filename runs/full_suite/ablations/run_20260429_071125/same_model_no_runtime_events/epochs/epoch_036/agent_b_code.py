def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        # No resources: keep distance from opponent while staying toward center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best, bestv = (0, 0), -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = king(nx, ny, ox, oy) * 3 - (king(nx, ny, cx, cy))
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    # Score resources based on whether we are competitive vs opponent.
    # Prefer resources where our distance is <= opponent distance; otherwise still allow if none competitive.
    competitive = []
    for rx, ry in resources:
        ds = king(sx, sy, rx, ry)
        do = king(ox, oy, rx, ry)
        competitive.append((ds <= do, ds, do, rx, ry))
    any_comp = any(c[0] for c in competitive)

    target = None
    best_key = None
    for is_comp, ds, do, rx, ry in competitive:
        if any_comp and not is_comp:
            continue
        # Key: minimize our distance, then maximize advantage (opponent farther), then deterministic coordinate tie-break.
        key = (0 if is_comp else 1, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    tx, ty = target

    # Choose move that minimizes our distance to target; tie-break: maximize distance from opponent.
    best, bestd, bestadv = [0, 0], 10**9, -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = king(nx, ny, tx, ty)
        adv = king(nx, ny, ox, oy)  # bigger is better
        if d < bestd or (d == bestd and adv > bestadv) or (d == bestd and adv == bestadv and (dx, dy) < (best[0], best[1])):
            bestd, bestadv, best = d, adv, [dx, dy]
    return best