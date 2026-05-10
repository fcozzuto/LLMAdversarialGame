def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    sr = str(observation.get("self_role") or "").lower()
    is_evader = not (("pursuer" in sr) or ("pred" in sr) or ("catch" in sr) or ("hunter" in sr))

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    tx, ty = (max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy)) if is_evader else (ox, oy))

    def neigh_obs(x, y):
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in obstacles:
                    cnt += 1
        return cnt

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if nx == ox and ny == oy:
            val = -10**9 if is_evader else 10**9
        else:
            dist = abs(nx - ox) + abs(ny - oy)
            corner_bias = abs(nx - tx) + abs(ny - ty)
            # For evader: maximize dist, then maximize corner_bias (stay far from target corner-approach), and avoid obstacle-adjacent.
            # For pursuer: minimize dist, then minimize corner_bias, and avoid obstacle-adjacent.
            obs_pen = neigh_obs(nx, ny)
            if is_evader:
                val = (dist * 1000) + (corner_bias * 10) - obs_pen
            else:
                val = (-dist * 1000) + (-corner_bias * 10) - obs_pen
        # Deterministic tie-break: prefer earlier move in list (already deterministic).
        if bestv is None or val > bestv:
            bestv = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]