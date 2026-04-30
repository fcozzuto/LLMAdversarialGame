def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b):
        d = abs(a[0] - b[0])
        e = abs(a[1] - b[1])
        return d if d > e else e

    cur_res = resources[0] if resources else None
    if resources:
        cur_res = min(resources, key=lambda p: (cheb((sx, sy), p), p[0], p[1]))

    best = (-10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if resources:
            rn = min(resources, key=lambda p: (cheb((nx, ny), p), p[0], p[1]))
            res_score = -cheb((nx, ny), rn)
        else:
            res_score = 0
        opp_score = cheb((nx, ny), (ox, oy))
        score = res_score + 0.1 * opp_score
        if score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]