def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def min_obs_dist(px, py):
        if not obstacles:
            return 999
        best = 999
        for ax, ay in obstacles:
            d = cheb(px, py, ax, ay)
            if d < best:
                best = d
        return best

    # Pick a target resource where we have a distance advantage over opponent.
    best_t = resources[0]
    best_gap = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        gap = sd - od  # smaller (more negative) is better for us
        if best_gap is None or gap < best_gap or (gap == best_gap and sd < cheb(sx, sy, best_t[0], best_t[1])):
            best_gap = gap
            best_t = (tx, ty)

    tx, ty = best_t

    # Evaluate all possible moves by next-position value.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_us = cheb(nx, ny, tx, ty)
        # Encourage staying on/near a resource path while discouraging moving close to obstacles.
        od = cheb(ox, oy, tx, ty)
        obs_pen = 0
        md = min_obs_dist(nx, ny)
        if md <= 1:
            obs_pen = 8
        elif md == 2:
            obs_pen = 3

        # Also bias towards moves that (likely) keep opponent further from the target.
        # Opponent moves next; we approximate by current opponent distance.
        v = (d_us - od) * 10 + d_us + obs_pen

        if best_v is None or v < best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]