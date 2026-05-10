def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = p
            obs.add((int(x), int(y)))

    sr = str(observation.get("self_role", "")).lower()
    i_am_evader = ("evad" in sr) or ("escape" in sr) or ("runner" in sr) or ("evader" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            return -10**9
        if (nx, ny) in obs:
            return -10**9

        dist_op = abs(nx - ox) + abs(ny - oy)
        if i_am_evader:
            # maximize distance from pursuer; avoid obstacles
            best = dist_op * 2.0
            if obs:
                md = 10**9
                for bx, by in obs:
                    d = abs(nx - bx) + abs(ny - by)
                    if d < md:
                        md = d
                best -= 4.0 / (1 + md)
            # slight preference for progressing toward farthest corner (ties break)
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            best += 0.15 * (abs(nx - far[0]) + abs(ny - far[1]))
            return best - 0.03 * (dx * dx + dy * dy)
        else:
            # pursuer: minimize distance to evader; avoid obstacles
            best = -dist_op * 2.0
            if obs:
                md = 10**9
                for bx, by in obs:
                    d = abs(nx - bx) + abs(ny - by)
                    if d < md:
                        md = d
                best -= 4.0 / (1 + md)
            # slight preference to reduce position change (deterministic stabilization)
            return best - 0.02 * (dx * dx + dy * dy)

    best_val = -10**18
    best_move = [0, 0]
    # deterministic tie-break: order is fixed, keep first max
    for dx, dy in deltas:
        v = score_move(dx, dy)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move