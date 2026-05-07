def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        d = abs(x1 - x2) + abs(y1 - y2)
        return d

    if not resources:
        return [0, 0]

    res = [(int(x), int(y)) for x, y in resources]
    best_move = [0, 0]
    best_sc = -10**18

    opp_next_dist_cache = {}
    for tx, ty in res:
        md = 10**9
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < md:
                md = d
        opp_next_dist_cache[(tx, ty)] = md

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        opp_dist_me = man(nx, ny, ox, oy)
        best_res_sc = -10**18
        for tx, ty in res:
            myd = man(nx, ny, tx, ty)
            opd_next = opp_next_dist_cache[(tx, ty)]
            sc = (opd_next - myd) * 100 - myd
            if opd_next <= myd:
                sc -= 60  # strong contest penalty
            if sc > best_res_sc:
                best_res_sc = sc
        total_sc = best_res_sc - 0.25 * opp_dist_me
        if total_sc > best_sc:
            best_sc = total_sc
            best_move = [dx, dy]

    return best_move