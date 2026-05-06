def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    try:
        w = int(w); h = int(h)
    except:
        w = 8; h = 8
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_best = None
    # baseline for opponent closeness to resources
    best_res_opp = None
    for r in resources:
        d = md((ox, oy), r)
        if best_res_opp is None or d < opp_best:
            opp_best = d
            best_res_opp = r

    best_move = (0, 0)
    best_val = None
    best_my = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_total = None
        for r in resources:
            d_my = md((nx, ny), r)
            d_opp = md((ox, oy), r)
            val = d_my - d_opp  # smaller is better
            if my_total is None or val < my_total or (val == my_total and d_my < best_my):
                my_total = val
                best_my = d_my
                # prefer resources where we are relatively closer than opponent
        if my_total is None:
            continue
        if best_val is None or my_total < best_val or (my_total == best_val and (best_my is not None) and (best_my < (best_my if best_val == my_total else 10**9))):
            best_val = my_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]