def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    un_list = list(unclaimed)
    nearest_un = None
    if un_list:
        nearest_un = min(un_list, key=lambda c: dist((sx, sy), c))

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        val = 0.0
        if cell in self_terr:
            val += 0.15
        if cell in unclaimed:
            val += 1.25
        if cell in opp_terr:
            val += 1.65  # counterclaim by flipping

        adj_un = 0
        adj_opp = 0
        adj_self = 0
        for ddx, ddy in dirs:
            x, y = nx + ddx, ny + ddy
            if not inb(x, y) or (x, y) in obstacles:
                continue
            if (x, y) in unclaimed:
                adj_un += 1
            if (x, y) in opp_terr:
                adj_opp += 1
            if (x, y) in self_terr:
                adj_self += 1

        val += 0.20 * adj_un
        val += 0.08 * adj_self
        val -= 0.35 * adj_opp  # avoid walking into direct opponent territory influence

        if nearest_un is not None:
            d_now = dist((sx, sy), nearest_un)
            d_new = dist((nx, ny), nearest_un)
            val += 0.25 * (d_now - d_new)  # progress toward nearest unclaimed

        # push toward opponent only when we can also grab/pressure unclaimed
        d_opp = dist(cell, opp_pos)
        val += 0.06 * (dist((sx, sy), opp_pos) - d_opp)
        if cell in unclaimed:
            val += 0.10 * (7 - d_opp)

        # deterministic tie-break
        if val > best_val or (val == best_val and (dx, dy) < (best[0], best[1]) if best else True):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]