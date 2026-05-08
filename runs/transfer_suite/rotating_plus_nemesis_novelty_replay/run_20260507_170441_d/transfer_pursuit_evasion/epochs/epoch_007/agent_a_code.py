def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))

    resources = observation.get("resources", []) or []
    rpos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rpos.append((int(r[0]), int(r[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best = (float("-inf"), 0, 0)
    has_res = len(rpos) > 0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if has_res:
            curd = 10**9
            nd = 10**9
            for rx, ry in rpos:
                d0 = (sx - rx) * (sx - rx) + (sy - ry) * (sy - ry)
                d1 = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if d0 < curd: curd = d0
                if d1 < nd: nd = d1
            score += (curd - nd) * 3
            score += -nd * 0.01
        else:
            score += -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.01

        od = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score += od * 0.002  # stay away from opponent

        if (dx, dy) == (0, 0):
            score -= 0.001  # slight bias to move when tied

        if score > best[0]:
            best = (score, dx, dy)

    if best[1] == 0 and best[2] == 0:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
    return [int(best[1]), int(best[2])]