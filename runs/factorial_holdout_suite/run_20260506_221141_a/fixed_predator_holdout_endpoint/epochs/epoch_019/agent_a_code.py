def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def parse_xy(p):
        if isinstance(p, dict):
            if "position" in p:
                p = p["position"]
            elif "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return int(p[0]), int(p[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            x, y = parse_xy(p)
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
        except Exception:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def king(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    best = (-10**18, 0, 0)
    if resources:
        for p in resources:
            try:
                tx, ty = parse_xy(p)
            except Exception:
                continue
            ds = king(sx, sy, tx, ty)
            do = king(ox, oy, tx, ty)
            adv = do - ds
            if adv > best[0]:
                best = (adv, tx, ty)

        tx, ty = best[1], best[2]
    else:
        tx, ty = cx, cy

    bestv = -10**18
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue
        dself = king(nx, ny, tx, ty)
        dobj = king(ox, oy, tx, ty)
        v = (dobj - dself) * 10 - dself
        v += 0.05 * king(nx, ny, ox, oy)  # slight spread
        if v > bestv or (v == bestv and (dx, dy) < bestm):
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]