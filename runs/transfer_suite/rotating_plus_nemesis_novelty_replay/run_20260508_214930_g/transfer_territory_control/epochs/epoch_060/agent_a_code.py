def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    my_t = set(tuple(p) for p in (observation.get("self_territory") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    if ox == sx and oy == sy:
        tx, ty = (w // 2, h // 2)
    else:
        # Prefer unclaimed near opponent; otherwise toward center
        if unclaimed:
            unclaimed.sort(key=lambda p: (abs(p[0] - ox) + abs(p[1] - oy), abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
            tx, ty = unclaimed[0]
        else:
            tx, ty = (w // 2, h // 2)

    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        sc = -d
        if (nx, ny) in opp_t:
            sc += 8
        if (nx, ny) in my_t:
            sc -= 1
        if unclaimed:
            if (nx, ny) in set(unclaimed[:50]):
                sc += 6
        if (dx, dy) == (0, 0):
            sc -= 0.2
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]