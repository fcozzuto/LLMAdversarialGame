def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    res_set = set((p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_cost = None

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if res_set and (sx, sy) in res_set:
        return [0, 0]

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        if (nx, ny) in res_set:
            return [mdx, mdy]
        if res_set:
            dres = min(man(nx, ny, rx, ry) for rx, ry in res_set)
        else:
            dres = man(nx, ny, w // 2, h // 2)
        dopp = man(nx, ny, ox, oy)
        cost = dres * 2 - dopp
        if best_cost is None or cost < best_cost or (cost == best_cost and (mdx, mdy) < best):
            best_cost = cost
            best = (mdx, mdy)

    if best is not None:
        return [best[0], best[1]]

    # Fallback: deterministic move toward center if all blocked
    tx, ty = w // 2, h // 2
    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)
    if valid(sx + dx, sy):
        return [dx, 0]
    if valid(sx, sy + dy):
        return [0, dy]
    if valid(sx, sy):
        return [0, 0]
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if valid(nx, ny):
            return [mdx, mdy]
    return [0, 0]