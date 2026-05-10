def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    my_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    their_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obs = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    steps = [(dx, dy) for dx, dy in dirs if dx != 0 or dy != 0]

    opp_adj = set()
    for x, y in their_terr:
        for dx, dy in steps:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in unclaimed:
                opp_adj.add((nx, ny))

    targets = list(opp_adj) if opp_adj else list(unclaimed)
    if not targets:
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - b) + abs(c - d)

    # Choose best immediate target (deterministic)
    tx, ty = None, None
    best_key = None
    for x, y in targets:
        d = manh(sx, x, sy, y)
        # Prefer closer, then prefer those nearer to the opponent (edge contest)
        key = (d, manh(ox, x, oy, y), x, y)
        if best_key is None or key < best_key:
            best_key = key
            tx, ty = x, y

    # Evaluate 9 possible moves with a local heuristic and obstacle avoidance
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            # engine will keep in place if invalid; penalize such moves so we avoid them deterministically
            score = -10**12
        else:
            # primary: reduce distance to chosen target
            prevd = manh(sx, tx, sy, ty)
            newd = manh(nx, tx, ny, ty)
            score = (prevd - newd) * 100

            # secondary: if we can flip opponent territory, value it heavily
            if (nx, ny) in their_terr:
                score += 800

            # secondary: reward stepping into unclaimed
            if (nx, ny) in unclaimed:
                score += 80

            # secondary: keep moving in direction that also pressures opponent edge
            score += -manh(nx, ox, ny, oy)

            # mild preference for not retracing inside own territory cycles: prefer expanding frontier
            if (nx, ny) in my_terr:
                score -= 5

            # add tie-breaker for determinism
            score += -(abs(dx) + abs(dy)) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]