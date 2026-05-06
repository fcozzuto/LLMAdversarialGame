def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))
    if not rlist:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d_center = abs(nx - cx) + abs(ny - cy)
            d_opp = md(nx, ny, ox, oy)
            v = d_center - 0.2 * d_opp
            if bestv is None or v < bestv or (v == bestv and (nx, ny) < best):
                bestv = v
                best = (nx, ny)
        if best is None:
            return [0, 0]
        return [best[0] - sx, best[1] - sy]

    alpha = 0.65
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # choose a resource that is best for us from this candidate position,
        # and prefer states where the opponent is far from that resource.
        best_self = None
        best_res = None
        for rx, ry in rlist:
            d_self = md(nx, ny, rx, ry)
            if best_self is None or d_self < best_self or (d_self == best_self and (rx, ry) < best_res):
                best_self = d_self
                best_res = (rx, ry)
        rx, ry = best_res
        d_opp = md(ox, oy, rx, ry)
        d_now_opp = md(nx, ny, ox, oy)

        # primary: minimize (our distance - alpha * their distance to same target)
        # secondary: avoid getting too close to opponent unless it's favorable.
        val = best_self - alpha * d_opp + 0.05 * d_now_opp

        if best_val is None or val < best_val or (val == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]