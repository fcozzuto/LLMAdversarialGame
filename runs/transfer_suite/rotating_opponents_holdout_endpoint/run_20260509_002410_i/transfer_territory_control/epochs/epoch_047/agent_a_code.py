def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    # Pick target deterministically: nearest unclaimed, else nearest opponent territory, else center.
    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    elif opp_t:
        tx, ty = min(opp_t, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    def score(nx, ny):
        d = abs(tx - nx) + abs(ty - ny)
        if (nx, ny) in opp_t:
            d += 100000
        if (nx, ny) in self_t:
            d -= 3
        if (nx, ny) in unclaimed:
            d -= 2
        return d

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        s = score(nx, ny)
        if best is None or s < best[0] or (s == best[0] and (dx, dy) < best[1]):
            best = (s, (dx, dy))
    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]