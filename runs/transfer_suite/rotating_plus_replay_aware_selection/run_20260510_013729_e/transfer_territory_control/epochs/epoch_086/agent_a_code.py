def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = observation.get("self_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    self_set = set()
    for p in self_t:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_set.add((int(p[0]), int(p[1])))

    un_list = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs:
                un_list.append((x, y))
    if not un_list:
        opp_t = observation.get("opponent_territory") or []
        for p in opp_t:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if (x, y) not in obs:
                    un_list.append((x, y))
    if not un_list:
        return [0, 0]

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    yield nx, ny

    frontier = []
    if self_set:
        for (x, y) in un_list:
            for nx, ny in neigh8(x, y):
                if (nx, ny) in self_set:
                    frontier.append((x, y))
                    break

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    targets = frontier if frontier else un_list

    def score_cell(tx, ty):
        d = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
        center_bias = (tx - cx) * (tx - cx) + (ty - cy) * (ty - cy)
        return d + 0.15 * center_bias

    best = None
    best_sc = None
    for (tx, ty) in targets:
        sc = score_cell(tx, ty)
        if best_sc is None or sc < best_sc or (sc == best_sc and (tx, ty) < best):
            best_sc = sc
            best = (tx, ty)
    tx, ty = best

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = []
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                dist = abs(tx - nx) + abs(ty - ny)
                moves.append((dist, nx, ny, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], abs(t[3]) + abs(t[4]), t[1], t[2], t[3], t[4]))
    _, _, _, mdx, mdy = moves[0]
    return [int(mdx), int(mdy)]