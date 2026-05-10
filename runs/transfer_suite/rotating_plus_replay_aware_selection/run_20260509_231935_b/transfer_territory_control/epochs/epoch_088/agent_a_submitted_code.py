def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inside(x, y) and (x, y) not in obs

    targets = observation.get("unclaimed_cells") or []
    tlist = []
    for p in targets:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                tlist.append((x, y))

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = (10**18, None)

    if tlist:
        nx0, ny0 = sx, sy
        # nearest target distance for current position
        best_t = min((md(sx, sy, x, y), x, y) for (x, y) in tlist)
        curd = best_t[0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # use nearest target from that move
            nd, _, _ = min((md(nx, ny, x, y), x, y) for (x, y) in tlist)
            score = (nd, -((sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)), abs(dx) + abs(dy), dx, dy)
            if score < best[0]:
                best = (score, [dx, dy])
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            # maximize distance from opponent
            dd = md(nx, ny, ox, oy)
            # slight preference to progress toward center
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            prog = md(nx, ny, int(cx), int(cy))
            score = (-dd, prog, abs(dx) + abs(dy), dx, dy)
            if score < best[0]:
                best = (score, [dx, dy])

    return best[1] if best[1] is not None else [0, 0]