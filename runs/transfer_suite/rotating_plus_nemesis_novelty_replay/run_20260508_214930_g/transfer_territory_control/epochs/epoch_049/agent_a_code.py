def choose_move(observation):
    w = observation.get("grid_width") or 8
    h = observation.get("grid_height") or 8
    sx, sy = observation.get("self_position") or (0, 0)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    resources = list(observation.get("resources") or [])
    rem = observation.get("remaining_resource_count")
    if rem is None:
        rem = len(resources)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(x, y):
        if (x, y) in obstacles:
            return -10**9
        s = 0
        if (x, y) in unclaimed:
            s += 8
        if (x, y) in self_t:
            s += 2
        if (x, y) in opp_t:
            s -= 6
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in unclaimed:
                    s += 1
                if (x + ax, y + ay) in opp_t:
                    s -= 1
        if resources:
            best = 10**9
            for rx, ry, *rest in resources:
                best = min(best, abs(rx - x) + abs(ry - y))
            s += max(0, 4 - best // 2)
        if rem is not None and rem <= 2 and (x, y) in unclaimed:
            s += 3
        return s

    best_move = (0, 0)
    best_score = cell_score(sx, sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = cell_score(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]