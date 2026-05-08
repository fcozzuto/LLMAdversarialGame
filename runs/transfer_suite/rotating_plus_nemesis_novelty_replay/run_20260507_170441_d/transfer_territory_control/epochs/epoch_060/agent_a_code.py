def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
        except:
            pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    cx, cy = w // 2, h // 2
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        if res:
            dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
        else:
            dres = abs(nx - cx) + abs(ny - cy)

        dopp = abs(nx - ox) + abs(ny - oy)
        score = (-dres) + 0.15 * dopp  # go toward resources, slightly keep distance

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]