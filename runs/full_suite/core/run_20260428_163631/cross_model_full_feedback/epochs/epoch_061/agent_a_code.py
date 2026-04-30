def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    res = []
    res_set = set()
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
                res_set.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    oppd_now = md(sx, sy, ox, oy)

    best = None
    best_val = -10**18
    for dx, dy, nx, ny in legal:
        # Immediate resource is always best
        if (nx, ny) in res_set:
            return [dx, dy]

        # Evaluate best target resource for this next position
        if res:
            self_to_res = min(md(nx, ny, rx, ry) for rx, ry in res)
            opp_to_res = min(md(ox, oy, rx, ry) for rx, ry in res)
            # For a chosen target, prefer where we are closer than opponent
            # and where opponent is not simultaneously advantaged.
            gap = -10**18
            for rx, ry in res:
                d_me = md(nx, ny, rx, ry)
                d_opp = md(ox, oy, rx, ry)
                # If opponent can reach much faster, avoid
                v = (d_opp - d_me) - 0.15 * md(nx, ny, rx, ry)
                if v > gap:
                    gap = v
            # Avoid getting too close to opponent unless we are also near a resource
            opp_close_pen = 0.0
            nd = md(nx, ny, ox, oy)
            if nd <= 2 and not opp_to_res <= self_to_res:
                opp_close_pen = (2 - nd) * 2.5
            center = -0.03 * (abs(nx - cx) + abs(ny - cy))
            val = (gap * 10.0) + (-0.2 * self_to_res) + (0.08 * oppd_now) + center - opp_close_pen
        else:
            # If no resources visible, keep away from opponent and drift toward center
            nd = md(nx, ny, ox, oy)
            center = -0.03 * (abs(nx - cx) + abs(ny - cy))
            val = 1.2 * nd + center

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best