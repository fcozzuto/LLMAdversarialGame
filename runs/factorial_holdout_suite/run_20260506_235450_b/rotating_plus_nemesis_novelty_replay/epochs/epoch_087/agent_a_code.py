def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_known = ox is not None and oy is not None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy, nx, ny in valid:
            self_gain = -(abs(nx - cx) + abs(ny - cy))
            opp_pen = 0
            if opp_known:
                opp_pen = 0.2 * (abs(nx - ox) + abs(ny - oy))
            sc = self_gain - opp_pen
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best_score = (-10**18, 0, 0)
    for dx, dy, nx, ny in valid:
        best_here = -10**18
        for r in resources:
            try:
                rx, ry = r
            except:
                continue
            d_self = abs(rx - nx) + abs(ry - ny)
            if d_self == 0:
                d_self = 0
            if opp_known:
                d_opp = abs(rx - ox) + abs(ry - oy)
            else:
                d_opp = d_self + 3  # unknown opponent: assume not closer
            # Prefer resources we can reach earlier; also prefer being closer overall.
            # If we are not ahead, still choose a move that improves our lead margin.
            lead = d_opp - d_self
            sc = (lead * 1000) - d_self + (-0.01) * (rx * 0 + ry * 0)
            if sc > best_here:
                best_here = sc
        # Tie-break: slightly prefer moves that reduce average distance to visible resources.
        avg_dist = 0
        cnt = 0
        for r in resources:
            try:
                rx, ry = r
            except:
                continue
            avg_dist += abs(rx - nx) + abs(ry - ny)
            cnt += 1
        if cnt:
            avg_dist /= cnt
        total = best_here - 0.05 * avg_dist
        if total > best_score[0]:
            best_score = (total, dx, dy)

    return [best_score[1], best_score[2]]