def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dsq(a, b, c, d):
        dx, dy = a - c, b - d
        return dx*dx + dy*dy

    # Pick a deterministic target: resource where we have best relative reach vs opponent.
    if not resources:
        # No resources visible: move to maximize distance while avoiding obstacles.
        best = None
        bestv = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = dsq(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    best_res = resources[0]
    best_metric = 10**18
    for rx, ry in resources:
        m = dsq(sx, sy, rx, ry) - 0.9 * dsq(ox, oy, rx, ry)
        if m < best_metric:
            best_metric = m
            best_res = (rx, ry)

    tx, ty = best_res

    # Evaluate candidate moves toward target, breaking ties with safety (distance from opponent).
    best = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        myd = dsq(nx, ny, tx, ty)
        opd = dsq(nx, ny, ox, oy)
        # Core: decrease distance to target, but only if opponent isn't clearly dominating it.
        core = -myd
        # Safety: prefer being farther from opponent (discourage getting trapped/contested).
        safe = 0.03 * opd
        # Also slightly discourage moves that worsen relative race to the target.
        rel = 0.001 * (dsq(sx, sy, tx, ty) - myd)

        score = core + safe + rel
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]