def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for c in obstacles:
        if c is not None and len(c) >= 2:
            try:
                obs.add((int(c[0]), int(c[1])))
            except:
                pass

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    own = set()
    for x, y in self_t:
        if x is not None and y is not None:
            own.add((int(x), int(y)))
    unq = set()
    for x, y in unclaimed:
        if x is not None and y is not None:
            unq.add((int(x), int(y)))
    opp = set()
    for x, y in opp_t:
        if x is not None and y is not None:
            opp.add((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Prefer capturing unclaimed, then avoid moving into opponent territory.
        score = 0
        if (nx, ny) in unq:
            score += 2000
        if (nx, ny) in opp:
            score -= 500
        if (nx, ny) in own:
            score += 50
        # Prefer increasing distance from opponent.
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_self = abs(nx - sx) + abs(ny - sy)
        score += 5 * d_opp
        score -= 10 * d_self
        # Deterministic tie-break.
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]