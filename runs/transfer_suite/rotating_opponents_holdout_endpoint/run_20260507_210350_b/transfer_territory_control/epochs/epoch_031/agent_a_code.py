def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_xy_list(v):
        out = []
        if not v:
            return out
        for p in v:
            try:
                x, y = p[0], p[1]
                out.append((int(x), int(y)))
            except Exception:
                pass
        return out

    obstacles = set(to_xy_list(observation.get("obstacles")))
    unclaimed = set(to_xy_list(observation.get("unclaimed_cells")))
    resources = set(to_xy_list(observation.get("resources")))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_s = None
    for dx, dy, nx, ny in cand:
        our_d_op = md(nx, ny, ox, oy)

        res_bonus = 0
        if (nx, ny) in resources:
            res_bonus = 3

        un_bonus = 0
        if (nx, ny) in unclaimed:
            un_bonus = 5

        # Distance to nearest resource/unclaimed (small, deterministic scan)
        near = 999999
        near_kind = 0
        for p in resources:
            d = md(nx, ny, p[0], p[1])
            if d < near:
                near = d
                near_kind = 1
        for p in unclaimed:
            d = md(nx, ny, p[0], p[1])
            if d < near:
                near = d
                near_kind = 2

        opp_near = 999999
        for p in resources:
            d = md(ox, oy, p[0], p[1])
            if d < opp_near:
                opp_near = d
        for p in unclaimed:
            d = md(ox, oy, p[0], p[1])
            if d < opp_near:
                opp_near = d

        # Prefer cells where we are closer to targets than opponent is.
        s = 2 * (opp_near - near) + un_bonus + res_bonus - 0.05 * our_d_op
        if best is None or s > best_s:
            best = (dx, dy)
            best_s = s

    return [int(best[0]), int(best[1])]