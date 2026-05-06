def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = r[0], r[1]
            if inb(rx, ry) and (rx, ry) not in obs:
                targets.append((rx, ry))

    if not targets:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = sx + dx, sy + dy
            if not blocked(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_val = None
    for rx, ry in targets:
        ds = md(rx, ry, sx, sy)
        do = md(rx, ry, ox, oy)
        # higher is better: we want resources where we are closer than opponent
        val = (do - ds) * 100000 - ds
        if best_val is None or val > best_val or (val == best_val and (rx, ry) < best):
            best_val = val
            best = (rx, ry)

    tx, ty = best
    # choose among valid 8-neighborhood (including stay) the move that reduces distance to target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    chosen = [0, 0]
    chosen_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = md(nx, ny, tx, ty)
        # tie-break deterministically: prefer closer, then lexicographically smaller move
        if chosen_dist is None or d < chosen_dist or (d == chosen_dist and (dx, dy) < tuple(chosen)):
            chosen_dist = d
            chosen = [dx, dy]
    if chosen_dist is None:
        return [0, 0]
    return chosen