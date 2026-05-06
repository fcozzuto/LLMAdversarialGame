def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        # deterministic drift toward center
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if free(sx + dx, sy + dy):
            return [dx, dy]
        if free(sx + dx, sy):
            return [dx, 0]
        if free(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    # choose neighbor move that maximizes advantage to secure a resource
    best = None
    best_key = None
    opp_pos = (ox, oy)
    self_pos = (sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        my_pos = (nx, ny)
        # evaluate best resource from this tentative position
        # advantage: (opp_dist - my_dist) and closeness priority
        local_best = None
        local_key = None
        for rx, ry in res:
            cell = (rx, ry)
            d_self = dist(my_pos, cell)
            d_opp = dist(opp_pos, cell)
            # If we are already closer, strongly prefer; otherwise still prefer "nearly contestable"
            adv = d_opp - d_self
            # slight preference for nearer resources and for breaking ties toward lower coordinates
            key = (adv, -d_self, -rx, -ry)
            if local_key is None or key > local_key:
                local_key = key
                local_best = cell
        # global: maximize local_best key
        if best_key is None or local_key > best_key:
            best_key = local_key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]