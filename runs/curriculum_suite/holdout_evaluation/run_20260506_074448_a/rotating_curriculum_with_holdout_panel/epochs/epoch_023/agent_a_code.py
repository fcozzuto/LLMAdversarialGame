def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            center = min(nx, w - 1 - nx, ny, h - 1 - ny)
            t = (center, -abs(dx) - abs(dy))
            if best is None or t > best[0]:
                best = (t, dx, dy)
        if best is None:
            return [0, 0]
        return [int(best[1]), int(best[2])]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if resources:
            dself = None
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if dself is None or d < dself or (d == dself and (rx, ry) < best_key):
                    dself = d
                    best_key = (rx, ry)
            dread = man(nx, ny, ox, oy)
            t = (-(dself), dread, min(nx, w - 1 - nx, ny, h - 1 - ny), -abs(dx) - abs(dy))
        if best is None or t > best[0]:
            best = (t, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]