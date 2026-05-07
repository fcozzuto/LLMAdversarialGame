def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        for tx, ty in resources:
            ds = abs(tx - sx) + abs(ty - sy)
            do = abs(tx - ox) + abs(ty - oy)
            # Prefer resources we can reach first; otherwise still prefer proximity and "denial pressure" (far from opponent).
            score = (do - ds) * 3 - ds + (0.01 * (ty - oy) - 0.005 * (tx - ox))
            if best is None or score > best[0]:
                best = (score, tx, ty)
        _, tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    else:
        # If no visible resources, drift toward the nearest corner that is not blocked.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            ds = abs(cx - sx) + abs(cy - sy)
            do = abs(cx - ox) + abs(cy - oy)
            score = (do - ds) * 0.2 - ds
            if best is None or score > best[0]:
                best = (score, cx, cy)
        if best is None:
            return [0, 0]
        _, tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0)]

    # Deterministic obstacle-avoiding choice among best candidate moves.
    for mvx, mvy in candidates:
        nx, ny = sx + mvx, sy + mvy
        if inside(nx, ny):
            return [int(mvx), int(mvy)]

    return [0, 0]