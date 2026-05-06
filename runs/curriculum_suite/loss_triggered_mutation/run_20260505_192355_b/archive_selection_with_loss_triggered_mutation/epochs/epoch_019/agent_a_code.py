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

    res_raw = observation.get("resources", []) or []
    resources = []
    for r in res_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    dxdy = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        for dx, dy in dxdy:
            nx, ny = sx + dx, sy + dy
            if is_free(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_move = (0, 0)
    for dx, dy in dxdy:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue

        # Primary: maximize advantage over opponent for the best resource we can reach next.
        # Secondary: prefer closer own distance to that same resource.
        best_adv = -10**9
        best_own = 10**9
        for rx, ry in resources:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and self_d < best_own) or (adv == best_adv and self_d == best_own and (rx < sx or (rx == sx and ry < sy))):
                best_adv = adv
                best_own = self_d

        # Add a mild tie-break to keep motion purposeful: move toward the centroid of resources.
        cx = sum(r[0] for r in resources) / float(len(resources))
        cy = sum(r[1] for r in resources) / float(len(resources))
        centroid_dist = md(nx, ny, int(cx), int(cy))
        key = (best_adv, -best_own, -centroid_dist, nx, ny, dx, dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]