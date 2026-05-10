def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    res_list = observation.get("resources", []) or []
    resources = []
    for p in res_list:
        try:
            resources.append((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur = (int(sx), int(sy))

    targets = resources
    if not targets:
        targets = [((w - 1) // 2, (h - 1) // 2)]

    def score(nx, ny):
        # prefer reaching resources; avoid opponent; avoid obstacles via legality check before scoring
        best_res = 10**9
        for rx, ry in targets:
            d = abs(rx - nx) + abs(ry - ny)
            if d < best_res:
                best_res = d
        opp_d = abs(ox - nx) + abs(oy - ny)
        return best_res * 10 - opp_d

    best = None
    best_s = None
    for dx, dy in moves:
        nx, ny = cur[0] + dx, cur[1] + dy
        if blocked(nx, ny):
            continue
        s = score(nx, ny)
        if best_s is None or s < best_s or (s == best_s and (dx, dy) < best):
            best_s = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]