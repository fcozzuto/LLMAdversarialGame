def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def wall_dist(x, y):
        return min(x, y, (w - 1) - x, (h - 1) - y)

    def blocked_neighbors(x, y):
        # Count how many adjacent (8-neighborhood) cells are blocked by obstacles or walls.
        c = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                c += 1
        return c

    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        if nx == ox and ny == oy:
            if not is_evader:
                return [dx, dy]
            # If we are evader, avoid capture (same-cell is losing).
            score = -10**12
        else:
            ddx, ddy = nx - ox, ny - oy
            d2 = ddx * ddx + ddy * ddy
            wd = wall_dist(nx, ny)
            bn = blocked_neighbors(nx, ny)
            # Deterministic scaling: keep main objective as distance sign, refine with wall safety and local openness.
            if is_evader:
                score = (d2 * 10.0) + (wd * 0.6) - (bn * 0.35) - (0.01 * (nx - sx) * (nx - sx) + 0.01 * (ny - sy) * (ny - sy))
            else:
                score = (-d2 * 10.0) + (wd * 0.25) - (bn * 0.12) + (0.02 * (sx == nx and sy == ny))
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]