def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    frontier_adj_opp = set()
    if opp_t:
        for tx, ty in opp_t:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                    frontier_adj_opp.add((nx, ny))

    candidates = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in candidates:
        candidates.append((0, 0))
    best = None
    best_score = -10**18

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            s = -1000
        elif (nx, ny) in opp_t:
            s = 500 + 2 * dist((nx, ny), (ox, oy)) * (-1)
        else:
            s = 0
            if (nx, ny) in frontier_adj_opp:
                s += 50
            if (nx, ny) in unclaimed:
                s += 15
            if (nx, ny) in self_t:
                s += 3
            d = dist((nx, ny), (ox, oy))
            s += -d
            if opp_t and (nx, ny) in opp_t:
                s += 200
        if s > best_score or (s == best_score and (dx, dy) < best):
            best_score = s
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]