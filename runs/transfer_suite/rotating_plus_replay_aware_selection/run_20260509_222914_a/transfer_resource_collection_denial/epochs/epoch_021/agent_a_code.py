def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            rx, ry = p[0], p[1]
            res.append((rx, ry))
        except Exception:
            pass

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return (ax - bx if ax >= bx else bx - ax) + (ay - by if ay >= by else by - ay)

    if res:
        tx, ty = min(res, key=lambda p: (man(x, y, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = w // 2, h // 2

    best = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        dtar = man(nx, ny, tx, ty)
        dop = man(nx, ny, ox, oy)
        # Prefer getting closer to target; if opponent is close, also prefer moving away.
        score = (dtar, -dop, nx, ny)
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]