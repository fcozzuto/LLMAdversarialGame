def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = observation.get("resources") or []
    # normalize possible formats: list of (x,y) or dict-like
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res_list.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                p = r["position"]
                res_list.append((int(p[0]), int(p[1])))

    def cheb(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 if d1 > d2 else d2

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        opp_d = cheb(nx, ny, ox, oy)
        min_res_d = 10**9
        if res_list:
            for rx, ry in res_list:
                d = cheb(nx, ny, rx, ry)
                if d < min_res_d:
                    min_res_d = d
        # Heuristic: prefer increasing distance from opponent, and approaching nearest resource.
        # Deterministic tie-break by dx, then dy.
        res_term = 0
        if res_list:
            res_term = -min_res_d * 2
            if min_res_d == 0:
                res_term += 1000
        opp_term = opp_d * 3
        key = (-(opp_term + res_term), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]