def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    evader = ("evader" in sr) or ("runner" in sr)
    if not evader and ("evader" in orr) or ("runner" in orr):
        evader = False

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_list.append((int(r[0]), int(r[1])))

    def nearest_res_dist(x, y):
        if not res_list:
            return 0
        dmin = None
        for rx, ry in res_list:
            if free(rx, ry) or (rx, ry) not in obstacles:
                d = man(x, y, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
        return dmin or 0

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = man(nx, ny, ox, oy)
        resd = nearest_res_dist(nx, ny)
        val = dist if evader else -dist
        if res_list:
            val += (-resd if not evader else resd) * 0.01
        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best, best_val = [dx, dy], val
    return best if best is not None else [0, 0]