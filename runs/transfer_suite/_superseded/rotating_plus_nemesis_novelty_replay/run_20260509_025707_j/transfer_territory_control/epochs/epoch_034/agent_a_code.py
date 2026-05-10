def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (sx, sy))
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    unclaimed = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    self_territory = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_territory = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    myc = observation.get("self_territory_count", len(self_territory))
    opc = observation.get("opponent_territory_count", len(opp_territory))
    behind = myc < opc

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (10**18, 0, 0)

    if behind and opc > 0:
        targets = [observation.get("opponent_position", (ox, oy))]
        for tx, ty in targets:
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not ok(nx, ny):
                    continue
                score = d2((nx, ny), (tx, ty))
                if score < best[0]:
                    best = (score, dx, dy)
    else:
        if unclaimed:
            tx, ty = min(unclaimed, key=lambda p: d2((sx, sy), p))
        else:
            tx, ty = (ox, oy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = d2((nx, ny), (tx, ty)) + (10 if behind else 0)
            if score < best[0]:
                best = (score, dx, dy)

    if best[0] == 10**18:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]
    return [best[1], best[2]]