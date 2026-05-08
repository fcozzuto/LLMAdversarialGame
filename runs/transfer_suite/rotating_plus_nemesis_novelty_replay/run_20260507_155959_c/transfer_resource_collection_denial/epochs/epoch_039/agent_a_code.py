def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    if (sx, sy) in obs: return [0, 0]

    def dist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res: return [0, 0]

    # Move scoring: try to maximize lead over opponent for a resource next turn,
    # with extra weight when we can currently take the resource.
    best_move = (0, 0)
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -10**9
            for rx, ry in res:
                dself = dist(nx, ny, rx, ry)
                dopp = dist(ox, oy, rx, ry)
                lead = dopp - dself  # positive means we are closer than opponent
                # If opponent isn't already closer, strongly prefer that we get/keep lead.
                dself_now = dist(sx, sy, rx, ry)
                dopp_now = dist(ox, oy, rx, ry)
                take_bonus = 500 if dself_now <= dopp_now else 0
                vcur = lead * 1000 - dself + take_bonus
                if vcur > v: v = vcur
            if best_val is None or v > best_val:
                best_val = v
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]