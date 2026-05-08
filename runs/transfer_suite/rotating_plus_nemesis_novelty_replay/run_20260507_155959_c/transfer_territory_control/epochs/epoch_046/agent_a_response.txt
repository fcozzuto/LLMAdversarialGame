def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    unclaimed = set()
    for c in (observation.get("unclaimed_cells") or []):
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    opp_t = set()
    for c in (observation.get("opponent_territory") or []):
        if c and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                opp_t.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obs

    dirs = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx != 0 or dy != 0:
                dirs.append((dx, dy))

    def manh(x, y): return abs(x - ox) + abs(y - oy)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        gain = 0
        if (nx, ny) in opp_t:
            gain += 2
        if (nx, ny) in unclaimed:
            gain += 1
        # Encourage approaching opponent to force flips; slightly prefer reducing distance.
        score = gain * 10 - manh(nx, ny) * 0.2
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]