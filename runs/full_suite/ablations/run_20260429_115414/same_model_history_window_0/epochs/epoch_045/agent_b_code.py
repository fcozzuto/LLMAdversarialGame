def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    if not resources:
        # No resources: move to increase distance from opponent, with slight bias to center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = d2(nx, ny, ox, oy) - 0.05 * d2(nx, ny, cx, cy)
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]

    # Pick a target resource based on how favorable it is relative to opponent.
    # Adaptation: alternate between chasing and "denying" by targeting the best-for-us resource
    # vs the best-for-them resource on odd turns.
    best_idx = 0
    bestv = -10**18
    for i, (rx, ry) in enumerate(resources):
        ds = d2(sx, sy, rx, ry)
        do = d2(ox, oy, rx, ry)
        favor = (do - ds)  # higher means we're closer than opponent
        if observation.get("turn_index", 0) % 2 == 1:
            favor = -favor  # deny mode: prefer resources where opponent is relatively close
        if favor > bestv:
            bestv, best_idx = favor, i
    tx, ty = resources[best_idx]

    best = None
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = d2(nx, ny, tx, ty)
        no = d2(ox, oy, tx, ty)
        if observation.get("turn_index", 0) % 2 == 0:
            v = (no - ns) - 0.01 * ns
        else:
            # In deny mode, prioritize positions that increase opponent's relative disadvantage
            # while still keeping near the target.
            v = -(ns - no) - 0.01 * ns
        # Small tie-break: avoid getting too close to obstacles via local proxy (none extra needed).
        if v > bestv:
            bestv, best = v, [dx, dy]
    return best if best is not None else [0, 0]