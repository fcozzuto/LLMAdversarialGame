def choose_move(observation):
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
        except Exception:
            x, y = p.get("x"), p.get("y")
        if isinstance(x, int) and isinstance(y, int) and inb(x, y):
            obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            x, y = p
        except Exception:
            x, y = p.get("x"), p.get("y")
        if isinstance(x, int) and isinstance(y, int) and inb(x, y):
            res.append((x, y))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in neigh:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_opp = manh(nx, ny, ox, oy)
        if res:
            d_res = min(manh(nx, ny, rx, ry) for rx, ry in res)
        else:
            d_res = 0
        key = (d_opp, -d_res, 0 if dx == 0 else 1, 0 if dy == 0 else 1, dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is not None:
        return best[1]
    return [0, 0]