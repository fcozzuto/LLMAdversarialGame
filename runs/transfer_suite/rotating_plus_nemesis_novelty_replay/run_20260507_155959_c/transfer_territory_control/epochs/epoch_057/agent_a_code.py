def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obs

    self_t = set()
    for c in (observation.get("self_territory") or []):
        if c is not None and len(c) >= 2:
            self_t.add((int(c[0]), int(c[1])))
    opp_t = set()
    for c in (observation.get("opponent_territory") or []):
        if c is not None and len(c) >= 2:
            opp_t.add((int(c[0]), int(c[1])))
    unclaimed = set()
    for c in (observation.get("unclaimed_cells") or []):
        if c is not None and len(c) >= 2:
            unclaimed.add((int(c[0]), int(c[1])))

    # Opponent centroid (deterministic)
    if opp_t:
        cx = sum(x for x, y in opp_t) / float(len(opp_t))
        cy = sum(y for x, y in opp_t) / float(len(opp_t))
    else:
        cx, cy = ox, oy

    center = (w // 2, h // 2)
    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        gain = 0
        if (nx, ny) in opp_t:
            gain = 2  # steal/flip
        elif (nx, ny) in unclaimed and (nx, ny) not in self_t:
            gain = 1  # new claim

        dist_opp = abs(nx - cx) + abs(ny - cy)
        dist_center = abs(nx - center[0]) + abs(ny - center[1])

        # Prefer stealing near opponent center-claimed area; otherwise expand to unclaimed while avoiding drifting too centrally
        score = (gain * 1000) - (dist_opp * 3) - (dist_center * 0.7)
        if (nx, ny) in self_t:
            score -= 5  # don't waste moves re-occupying own cells

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [int(dx), int(dy)]

    return best_move