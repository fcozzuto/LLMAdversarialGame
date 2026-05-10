def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick a target where we can arrive earlier than opponent; otherwise, pick closest remaining.
    best_t = None
    best_key = None
    for r in resources:
        tx, ty = int(r[0]), int(r[1])
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Prefer earlier arrival; if close, prefer farther from opponent (reduces contest).
        key = (od - sd, -sd, -od, tx, ty)  # maximize first components
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Local step scoring: move to reduce our distance to target, while discouraging stepping near obstacles,
    # and slightly increasing opponent distance to the same target (counter row-sweeping).
    def near_obstacle(nx, ny):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in obstacles:
                    p += 1
        return p

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # Encourage improving vs staying; penalize obstacle proximity and worsening our distance.
        val = (-myd, (opd - myd), -near_obstacle(nx, ny), -abs(oy - ty), -abs(ox - tx), dx, dy)
        # We want lexicographically largest; construct accordingly by flipping sign where needed already.
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move