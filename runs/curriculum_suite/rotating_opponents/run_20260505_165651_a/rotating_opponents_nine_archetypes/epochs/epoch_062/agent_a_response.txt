def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def clamp01(v):
        if v < 0:
            return 0
        if v > 1:
            return 1
        return v

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_val = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            d1 = man(nx, ny, cx, cy)
            d2 = man(nx, ny, ox, oy)
            val = (-d1, d2, dx, dy)
            if best_val is None or val < best_val:
                best_val, best_move = val, [dx, dy]
        return best_move

    best_overall = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Contest-aware resource target
        best_claim = -10**9
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            # Encourage grabbing if we're closer, but penalize moves that give opponent advantage soon.
            claim = (d_op - d_me) * 3 - d_me
            # If opponent can reach in same turn window, reduce attractiveness.
            if d_op <= d_me:
                claim -= (d_me + 2)
            best_claim = claim if claim > best_claim else best_claim

        # Safety: stay away while still progressing to resources
        dist_opp = man(nx, ny, ox, oy)
        # Normalize via grid scale
        safety = (dist_opp - 2) * 1.5
        # Small tie-break to prefer not drifting aimlessly: use min distance to any resource
        min_d_res = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < min_d_res:
                min_d_res = d

        val = (best_claim + safety, -min_d_res, dx, dy)
        if best_overall is None or val > best_overall:
            best_overall, best_move = val, [dx, dy]

    return best_move