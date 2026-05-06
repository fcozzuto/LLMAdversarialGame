def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))
    if not targets:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: prefer moves with smallest dx, then dy order.
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Evaluate from next position against the best resource for us to contest.
        local_best = None
        for tx, ty in targets:
            if not legal(tx, ty):
                continue
            sd = man(nx, ny, tx, ty)
            od = man(ox, oy, tx, ty)
            # High when we are closer than opponent; otherwise reduce their advantage.
            v = (od - sd) * 10 - sd
            if local_best is None or v > local_best:
                local_best = v
        if local_best is None:
            continue
        # Small preference to reduce own distance to the best target.
        final_v = local_best
        if best_val is None or final_v > best_val:
            best_val = final_v
            best = (dx, dy)

    if best is None:
        # All blocked: attempt stay.
        return [0, 0]
    return [best[0], best[1]]