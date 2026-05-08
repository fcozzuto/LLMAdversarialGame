def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_sc = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = -dist(nx, ny, tx, ty) + 0.01 * dist(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # If already on a resource, just take it (stay).
    if (sx, sy) in obstacles:
        pass
    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    best_t = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources where we can arrive earlier; also prefer closer targets.
        # Deterministic tie-break: smaller (sd, od, rx, ry) after negating.
        key = (od - sd, -sd, -od, -(rx + 31 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    # If opponent is much closer to all, bias toward blocking by moving toward the best "contested" target.
    # (Still deterministic; captured in key selection above.)

    best_move = (0, 0)
    best_sc = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = dist(nx, ny, rx, ry)
        # Keep progress toward target, and slightly avoid squares that give opponent a big lead shift.
        # Bonus if this step reduces our distance.
        gain = (dist(sx, sy, rx, ry) - nd)
        odn = dist(nx, ny, rx, ry)  # our future distance used below
        oppd = dist(ox, oy, rx, ry)
        sc = gain * 10 + (-nd) + 0.01 * (oppd - odn)
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]