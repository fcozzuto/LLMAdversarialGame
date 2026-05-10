def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed_list = list(unclaimed)
    if unclaimed_list:
        nearest_un = min(unclaimed_list, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        nearest_un = (ox, oy)

    def adj_count_set(x, y, s):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in s:
                c += 1
        return c

    def cell_score(x, y):
        if (x, y) in opp_terr:
            v = 10
        elif (x, y) in unclaimed:
            v = 8
        elif (x, y) in self_terr:
            v = 2
        else:
            v = 0
        v += 2 * adj_count_set(x, y, unclaimed)
        v += 1 * adj_count_set(x, y, self_terr)
        v += 0.5 * adj_count_set(x, y, opp_terr)
        # Deterministic positioning preference:
        v += -0.05 * (abs(x - (w - 1) / 2.0) + abs(y - (h - 1) / 2.0))
        v += -0.1 * (abs(x - ox) + abs(y - oy))  # avoid being too close to sweeper
        # Prefer stepping toward nearest unclaimed
        v += -0.2 * (abs(x - nearest_un[0]) + abs(y - nearest_un[1]))
        return v

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        v = cell_score(nx, ny)
        key = (v, -abs(nx - ox) - abs(ny - oy), -abs(nx - nearest_un[0]) - abs(ny - nearest_un[1]), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]