def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = 0 if sx > (w - 1) / 2 else (w - 1)
        ty = 0 if sy > (h - 1) / 2 else (h - 1)
        best = (0, 0)
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -dist((nx, ny), (tx, ty))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd = 0
        # Evaluate the best resource we could claim next (relative to opponent)
        cur = (nx, ny)
        best_res = -10**18
        for rx, ry in resources:
            rd = (rx, ry)
            ds = dist(cur, rd)
            do = dist((ox, oy), rd)
            # Favor resources where we can beat/track opponent; penalize delay a bit.
            val = (do - ds) * 3 - ds
            # Small tie-break toward the most central-ish cells for stability.
            cx = rx - (w - 1) / 2
            cy = ry - (h - 1) / 2
            val -= int((cx * cx + cy * cy) * 0.02)
            if val > best_res:
                best_res = val
        sd = best_res
        # Extra preference for reducing immediate distance to the current best.
        if sd > bestv:
            bestv = sd
            best = (dx, dy)
    return [best[0], best[1]]