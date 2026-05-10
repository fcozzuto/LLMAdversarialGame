def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opT.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def mindist_to(points, x, y):
        if not points:
            return 10**9
        md = 10**9
        for px, py in points:
            d = abs(px - x) + abs(py - y)
            if d < md:
                md = d
        return md

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0
        if (nx, ny) in opT:
            score += 5000
        dres = mindist_to(res, nx, ny)
        if res:
            score += -100 * dres
        else:
            score += -10 * (abs(nx - cx) + abs(ny - cy))
        score += 2 * (abs(nx - ox) + abs(ny - oy))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move