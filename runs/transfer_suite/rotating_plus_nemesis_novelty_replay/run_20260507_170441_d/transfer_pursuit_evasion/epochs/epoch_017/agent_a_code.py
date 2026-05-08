def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Opponent moves to maximize distance from our next position
        opp_best_d = -1
        opp_best_pos = (ox, oy)
        for odx, ody in dirs:
            ax, ay = ox + odx, oy + ody
            if not ok(ax, ay):
                continue
            d = dist2(ax, ay, nx, ny)
            if d > opp_best_d or (d == opp_best_d and (ax, ay) < opp_best_pos):
                opp_best_d = d
                opp_best_pos = (ax, ay)

        ax, ay = opp_best_pos
        if (ax == nx and ay == ny):
            val = 10**9 + (dx * 3 + dy) * 0
        else:
            val = -dist2(nx, ny, ax, ay)

        # deterministic tie-break: prefer lower dx, then dy
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]