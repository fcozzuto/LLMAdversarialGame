def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    self_count = observation.get("scores", {}).get("self", observation.get("self_territory_count", len(self_terr)))
    opp_count = observation.get("scores", {}).get("opponent", observation.get("opponent_territory_count", len(opp_terr)))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    frontier = set()
    if self_terr and unclaimed:
        for x, y in self_terr:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed:
                    frontier.add((nx, ny))

    targets = sorted(frontier) if frontier else (sorted(unclaimed) if unclaimed else [])
    if targets:
        tx, ty = min(targets, key=lambda t: (dist((sx, sy), t), t[0], t[1]))
    else:
        tx, ty = (ox, oy)

    behind = (self_count < opp_count)
    if behind and opp_terr:
        tx2, ty2 = min(sorted(opp_terr), key=lambda t: (dist((sx, sy), t), t[0], t[1]))
        tx, ty = (tx2, ty2)

    best = None
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = -dist((nx, ny), (tx, ty))
        if behind:
            v += -0.2 * dist((nx, ny), (ox, oy))
        else:
            v += 0.05 * dist((nx, ny), (ox, oy))
        if v > best_val or (v == best_val and (dx, dy) < (best[0], best[1]) if best else True):
            best_val = v
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]