def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                moves.append((0, 0))
            else:
                if inb(nx, ny) and (nx, ny) not in obs:
                    moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        tx = w - 1 if ox < w // 2 else 0
        ty = h - 1 if oy < h // 2 else 0
        best = min(moves, key=lambda m: abs((sx + m[0]) - tx) + abs((sy + m[1]) - ty))
        return [best[0], best[1]]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    bestm, bestkey = None, None
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        my_nearest = 10**9
        max_margin = -10**9
        for rx, ry in resources:
            dself = man(nsx, nsy, rx, ry)
            dopp = man(ox, oy, rx, ry)
            if dself < my_nearest:
                my_nearest = dself
            margin = dopp - dself
            if margin > max_margin:
                max_margin = margin
        # Prefer largest positive margin (I beat opponent), then shortest my distance, then slightly toward center.
        mx = (nsx - cx) * (nsx - cx) + (nsy - cy) * (nsy - cy)
        key = (-max_margin, my_nearest, mx, dx, dy)
        if bestkey is None or key < bestkey:
            bestkey, bestm = key, (dx, dy)

    return [int(bestm[0]), int(bestm[1])]