def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def ti(v):
        try:
            return int(v)
        except:
            return 0

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = ti(sp[0]), ti(sp[1])
    ox, oy = ti(op[0]), ti(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                cells.append((x, y))
    if not cells:
        return [0, 0]

    # Choose target: prioritize resources we can reach earlier than opponent, breaking ties by larger score value proxy (earlier).
    # With obstacles, distances are Manhattan (fast deterministic heuristic).
    best = None
    for x, y in cells:
        sd = abs(x - sx) + abs(y - sy)
        od = abs(x - ox) + abs(y - oy)
        # Prefer (opponent_soon - self_soon) large; also prefer smaller self distance
        val = (od - sd) * 100 - sd
        if best is None or val > best[0] or (val == best[0] and (sd < best[1] or (sd == best[1] and (x, y) < best[2]))):
            best = (val, sd, (x, y))
    tx, ty = best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        sd2 = abs(tx - nx) + abs(ty - ny)
        od2 = abs(tx - ox) + abs(ty - oy)  # opponent fixed this turn
        # If move blocks path, obstacle avoidance via staying/other candidates occurs by scoring below
        # Also prevent "orbiting" by preferring progress on both axes toward target implicitly via sd2.
        val = (od2 - sd2) * 100 - sd2
        # Tiny deterministic bias to reduce oscillation: favor dx,dy closer to target direction signs.
        signx = 0 if tx == sx else (1 if tx > sx else -1)
        signy = 0 if ty == sy else (1 if ty > sy else -1)
        val += -((dx - signx) * (dx - signx) + (dy - signy) * (dy - signy))
        if bestm is None or val > bestm[0] or (val == bestm[0] and (dx, dy) < bestm[1]):
            bestm = (val, (dx, dy))
    if bestm is None:
        return [0, 0]
    return [bestm[1][0], bestm[1][1]]