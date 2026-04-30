def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose two targets: one for us, one for opponent, to create a deterministic "deny" pressure.
    center = ((w - 1) // 2, (h - 1) // 2)
    if resources:
        rs = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
        ro = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    else:
        rs = center
        ro = (w - 1 - center[0], h - 1 - center[1])

    best = (0, 0)
    best_val = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy

            d_us = cheb(nx, ny, rs[0], rs[1])
            d_us_now = cheb(sx, sy, rs[0], rs[1])

            d_op_to_ro = cheb(ox, oy, ro[0], ro[1])
            d_me_to_ro = cheb(nx, ny, ro[0], ro[1])
            d_me_to_op_target_now = cheb(sx, sy, ro[0], ro[1])

            # Greedy progress to our target + "deny" by moving closer to opponent's likely target.
            # Also slightly bias away from letting opponent get strictly closer than us.
            lead_now = d_us_now - d_op_to_ro
            lead_next = d_us - d_op_to_ro

            val = 0
            val += -d_us
            val += -0.55 * d_me_to_ro
            val += 0.25 * (lead_now - lead_next)
            # If we're equally far, prefer tighter approach toward center (break ties deterministically).
            val += -0.02 * cheb(nx, ny, center[0], center[1])

            if val > best_val or (val == best_val and (nx - sx, ny - sy) < best):
                best_val = val
                best = (nx - sx, ny - sy)

    return [int(best[0]), int(best[1])]