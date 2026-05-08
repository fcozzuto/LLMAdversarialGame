def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            x, y = int(x), int(y)
            if inb(x, y):
                obs.add((x, y))
        except Exception:
            pass

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    resources = []
    for p in (observation.get("resources") or []):
        try:
            x, y = p
            x, y = int(x), int(y)
            if ok(x, y):
                resources.append((x, y))
        except Exception:
            pass

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources or not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose a target where we can arrive sooner than opponent, else pick least-losing.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        d_self = dist(sx, sy, rx, ry)
        d_opp = dist(ox, oy, rx, ry)
        # Encourage earlier arrival; heavily prefer resources we can beat.
        beat = d_opp - d_self
        score = 1000 * beat - d_self
        # Slight penalty if target is "behind" opponent along both axes.
        if (rx - sx) * (rx - ox) > 0:
            score -= 3
        if (ry - sy) * (ry - oy) > 0:
            score -= 3
        if score > best_score or (score == best_score and (best is None or (rx, ry) < best)):
            best_score = score
            best = (rx, ry)

    rx, ry = best
    # Pick the move that reduces distance to target while also avoiding giving opponent a faster line.
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = dist(nx, ny, rx, ry)
        # Simulate opponent response: measure how close opponent would be to that target after we move.
        d_opp = dist(ox, oy, rx, ry)
        # Also consider if we move closer to opponent directly (shadow risk).
        d_to_opp = dist(nx, ny, ox, oy)
        # Deterministic tie-break: prefer smaller dx,dy ordering already fixed by list.
        val = -d_self + 0.2 * (d_opp - d_self) - 0.01 * d_to_opp
        cand.append((val, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(reverse=True)
    return [int(cand[0][1]), int(cand[0][2])]