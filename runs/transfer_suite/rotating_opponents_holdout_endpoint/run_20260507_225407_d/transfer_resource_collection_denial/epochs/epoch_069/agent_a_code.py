def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))
        except Exception:
            pass

    resources_raw = observation.get("resources") or []
    resources = []
    for p in resources_raw:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))
        except Exception:
            pass

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    bestv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy

        if resources:
            dres = min(md(nx, ny, rx, ry) for rx, ry in resources)
        else:
            dres = md(nx, ny, w // 2, h // 2)

        dop = md(nx, ny, ox, oy)
        # Prefer closer to resources, avoid being too close to opponent, stay centered if no resources.
        val = dres * 2 - dop
        if bestv is None or val < bestv or (val == bestv and (dx, dy) < best):
            bestv = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]