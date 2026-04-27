def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is None or len(p) < 2:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = [(int(r[0]), int(r[1])) for r in resources if r is not None and len(r) >= 2]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def score_at(nx, ny):
        if not res:
            # Prefer moving toward center early, stay if all else blocked.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return -man(nx, ny, cx, cy) + 0.15 * man(nx, ny, ox, oy)
        best = -10**9
        # Maximize "advantage" for grabbing a resource.
        for rx, ry in res:
            dmy = man(nx, ny, rx, ry)
            dop = man(ox, oy, rx, ry)
            # If opponent closer, still allow chasing if close enough to reach first after moving.
            adv = (dop - dmy)
            # Small preference for being close overall to some resource.
            clos = -0.12 * dmy
            # Mild tie-break away from opponent to reduce contesting region.
            anti = 0.03 * man(nx, ny, ox, oy)
            val = 10 * adv + clos + anti
            if val > best:
                best = val
        return best

    if not cand:
        return [0, 0]

    best_move = cand[0]
    best_val = score_at(best_move[2], best_move[3])
    # Deterministic tie-break: lower dx, then lower dy, then any.
    for dx, dy, nx, ny in cand:
        v = score_at(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = v
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]