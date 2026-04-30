def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sign(v):
        return (v > 0) - (v < 0)

    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        tx, ty = min(resources, key=lambda t: max(abs(t[0] - sx), abs(t[1] - sy)))
    else:
        tx, ty = cx, cy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        cur_dist = max(abs(sx - tx), abs(sy - ty))
        new_dist = max(abs(nx - tx), abs(ny - ty))
        opp_now = max(abs(sx - ox), abs(sy - oy))
        opp_new = max(abs(nx - ox), abs(ny - oy))
        score = (cur_dist - new_dist) * 10 + (opp_new - opp_now) * 3
        if resources and (nx, ny) in resources:
            score += 1000
        if best is None or score > bestv:
            bestv = score
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]