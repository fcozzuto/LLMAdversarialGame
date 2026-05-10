def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    is_evader = ("evad" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_obst_md(x, y):
        if not obs:
            return 99
        best = 99
        for bx, by in obs:
            d = abs(x - bx) + abs(y - by)
            if d < best:
                best = d
        return best

    # If near an obstacle, prefer moves that increase distance; if cornered, prioritize escape direction.
    target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy)) if is_evader else None

    best = (0, 0, -10**18)  # dx,dy,val
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d = dist2(nx, ny, ox, oy)
        obst = nearest_obst_md(nx, ny)
        obst_pen = 0
        if obst <= 1:
            obst_pen = 50
        elif obst <= 2:
            obst_pen = 18
        elif obst <= 3:
            obst_pen = 8

        if is_evader:
            # Maximize distance to pursuer and drift toward farthest corner; also avoid obstacles.
            corner_bias = 0
            if target_corner is not None:
                corner_bias = -dist2(nx, ny, target_corner[0], target_corner[1])
            # Slight preference for reducing pursuer's ability to line up: prefer staying on "diagonal" away.
            align = (nx - ox) * (sx - ox) + (ny - oy) * (sy - oy)
            val = d - 0.35 * corner_bias - obst_pen + 0.08 * align
        else:
            # Pursuer: minimize distance to evader; also avoid obstacles.
            obst_pen = obst_pen * 1.0
            # Prefer moves that reduce both x and y differences (diagonal chase).
            adx = abs(nx - ox) - abs(sx - ox)
            ady = abs(ny - oy) - abs(sy - oy)
            val = -d - obst_pen - 0.6 * (adx + ady)

        # Deterministic tie-breaker order already fixed by deltas; keep first best.
        if val > best[2]:
            best = (dx, dy, val)

    dx, dy, _ = best
    # If all moves invalid, stay (engine will keep us in place).
    return [int(dx), int(dy)]