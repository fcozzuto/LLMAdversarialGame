def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_resource():
        best = None
        best_key = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            diff = od - sd  # positive: we are closer or equal
            if diff >= 0:
                key = (0, -diff, sd, rx, ry)  # prefer not-behind and smaller sd
            else:
                key = (1, diff, sd, rx, ry)   # behind: least negative diff, then smaller sd
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_resource()

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # avoid stepping onto opponent (engine would keep us anyway, but this discourages)
        if nx == ox and ny == oy:
            continue
        self_to = man(nx, ny, tx, ty)
        opp_to = man(ox, oy, tx, ty)
        # tie-break: keep progress; if equal, slightly reduce opponent distance to prevent easy claims
        val = (self_to, -(opp_to - self_to))
        if best_val is None or val < best_val:
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]