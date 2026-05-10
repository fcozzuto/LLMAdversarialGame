def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_evader = ("evad" in self_role) or (("agent" in self_role) and ("evad" in opp_role))

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_move(nx, ny):
        # Use Chebyshev distance as capture is point-radius 0; tie-break with squared Euclidean
        dx, dy = abs(nx - ox), abs(ny - oy)
        cheb = dx if dx > dy else dy
        eu2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if self_is_evader:
            # prefer increasing distance, avoid moving into/adjacent to obstacles
            adj = 0
            for (bx, by) in obs:
                d = abs(nx - bx) + abs(ny - by)
                if d == 0:
                    return -10**9
                if d == 1:
                    adj -= 2
            # favor drifting toward far corner relative to pursuer (deterministic)
            corner_x = 0 if ox >= (w - 1) / 2 else (w - 1)
            corner_y = 0 if oy >= (h - 1) / 2 else (h - 1)
            corner_bias = -((nx - corner_x) * (nx - corner_x) + (ny - corner_y) * (ny - corner_y)) // 2
            return (cheb * 1000 + eu2) + adj + corner_bias
        else:
            # pursuer: minimize distance; also prefer not moving next to obstacles (since they block routes)
            adj = 0
            for (bx, by) in obs:
                d = abs(nx - bx) + abs(ny - by)
                if d == 0:
                    return -10**9
                if d == 1:
                    adj -= 3
            # small preference to approach along the more aligned axis
            align = 0
            if ox != sx:
                align -= abs((nx - sx) - (1 if ox > sx else -1))
            if oy != sy:
                align -= abs((ny - sy) - (1 if oy > sy else -1))
            return -(cheb * 1000 + eu2) + adj + align

    best = None
    best_val = None
    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        val = score_move(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]