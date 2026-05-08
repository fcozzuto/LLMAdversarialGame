def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    un = to_set("unclaimed_cells")

    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    # Precompute targets list for a cheap nearest distance heuristic
    targets = []
    if un:
        targets.append(min(un, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy)))
    if opp_t:
        targets.append(min(opp_t, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy)))
    if not targets:
        targets = [(ox, oy)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic tie-breaker order: fixed dirs order already
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        p = (nx, ny)

        val = 0.0
        if p in opp_t:
            val += 120.0  # flipping pressure
        elif p in un:
            val += 60.0   # claim new territory
        elif p in self_t:
            val += 10.0   # consolidate
        else:
            val += 5.0

        # Prefer moving away from opponent to resist sweeps
        val += 0.7 * (dist(p, (ox, oy)))

        # Also prefer improving toward a relevant target (unclaimed/opp)
        if targets:
            val += -0.05 * min(dist(p, t) for t in targets)

        # Small penalty for staying still (unless it helps avoid immediate conflict)
        if dx == 0 and dy == 0:
            val -= 6.0

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]