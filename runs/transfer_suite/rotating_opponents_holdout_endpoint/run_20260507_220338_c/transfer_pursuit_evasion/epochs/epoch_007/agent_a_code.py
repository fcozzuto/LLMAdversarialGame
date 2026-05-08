def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x0, y0 = observation.get("self_position", [0, 0])
    xo, yo = observation.get("opponent_position", [0, 0])
    x0 = int(x0); y0 = int(y0); xo = int(xo); yo = int(yo)

    obstacles = observation.get("obstacles", []) or []
    ox = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ox.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", None)
    res_list = []
    if isinstance(resources, (list, tuple)):
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) == 2:
                res_list.append((int(r[0]), int(r[1])))
    rem = observation.get("remaining_resource_count", None)
    have_res = bool(res_list) or (isinstance(rem, (int, float)) and rem > 0)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        da = a - c
        db = b - d
        return abs(da) if abs(da) > abs(db) else abs(db)

    best = None
    bestv = -10**18

    d_opp_now = cheb(x0, y0, xo, yo)
    near_opp = d_opp_now <= 2

    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if not in_bounds(nx, ny) or (nx, ny) in ox:
            continue
        d_opp = cheb(nx, ny, xo, yo)
        if have_res:
            d_res = 10**9
            for rx, ry in res_list:
                d = cheb(nx, ny, rx, ry)
                if d < d_res:
                    d_res = d
            if d_res == 10**9:
                score_res = 0
            else:
                score_res = 20 - 2 * d_res
        else:
            score_res = 0

        # If opponent is close, prefer escaping; otherwise prefer approaching opponent and resources.
        if near_opp:
            v = (3 * d_opp) + score_res
        else:
            v = (-2 * d_opp) + score_res

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = x0 + dx, y0 + dy
            if in_bounds(nx, ny) and (nx, ny) not in ox:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]