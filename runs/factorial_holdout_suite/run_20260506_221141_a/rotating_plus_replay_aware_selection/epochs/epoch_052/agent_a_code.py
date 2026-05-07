def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best = (0, 0)
    bestv = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = 0
            for r in resources:
                rx, ry = r[0], r[1]
                d1 = md(nx, ny, rx, ry)
                d2 = md(ox, oy, rx, ry)
                v += 20 * (d2 - d1) - d1
            if v > bestv:
                bestv = v
                best = (dx, dy)
    else:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -md(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)

    return [best[0], best[1]]