def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set((int(x), int(y)) for x, y in obs)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in legal:
        if (nx, ny) in resources:
            score = 10**9
        else:
            my_d = min(md(nx, ny, rx, ry) for rx, ry in resources)
            opp_d = md(ox, oy, nx, ny)
            score = my_d * 10 - opp_d
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]