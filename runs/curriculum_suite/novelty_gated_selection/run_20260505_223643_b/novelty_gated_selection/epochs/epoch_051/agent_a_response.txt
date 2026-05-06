def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def norm_pos(v):
        if isinstance(v, dict):
            if "position" in v and v["position"]:
                v = v["position"]
            else:
                if "x" in v and "y" in v:
                    return int(v["x"]), int(v["y"])
                return None
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return None

    obstacles = set()
    for item in observation.get("obstacles", []) or []:
        p = norm_pos(item)
        if p:
            x, y = p
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for item in observation.get("resources", []) or []:
        p = norm_pos(item)
        if p:
            x, y = p
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if not resources:
            # When no resources: keep distance and avoid moves that step toward opponent
            key = (0, manh((nx, ny), (ox, oy)), dx, dy)
            cand = key
        else:
            # Interception/contest heuristic:
            # prefer moves that reach some resource no later than opponent (or earlier),
            # with tie-break toward closer self and farther opponent.
            own_best = None
            for r in resources:
                sd = manh((nx, ny), r)
                od = manh((ox, oy), r)
                can = 1 if sd <= od else 0
                # prefer earlier/stronger take; also keep some backup options
                k = (can, -od, sd)
                if own_best is None or k < own_best[0]:
                    own_best = (k, r)
            can, neg_od, sd = own_best[0]
            # additional tie-break: reduce distance to the selected resource
            # and slightly avoid getting too close to opponent.
            od_sel = -neg_od
            opp_close = manh((nx, ny), (ox, oy))
            cand = (-can, sd, od_sel, opp_close, dx, dy)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[-2]), int(best[-1])]