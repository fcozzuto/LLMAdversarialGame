def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    self_t = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def adj8(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1

    def count_adj(cell, tset):
        x, y = cell
        c = 0
        for dx, dy in (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1):
            nx, ny = x + dx, y + dy
            if (nx, ny) in tset:
                c += 1
        return c

    best = None
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        d_opp = min((abs(nx - ox) + abs(ny - oy) for ox, oy in opp_t), default=999)
        near_self = count_adj(cell, self_t)
        near_opp = count_adj(cell, opp_t)

        if cell in opp_t:
            v = 140 - 2.0 * (abs(nx - sx) + abs(ny - sy)) - 3.0 * near_opp
        elif cell in unclaimed:
            v = 55 + 4.0 * near_self - 8.0 * near_opp - 0.25 * (abs(nx - sx) + abs(ny - sy))
        elif cell in self_t:
            v = 10 + 1.5 * near_self - 2.0 * near_opp
        else:
            v = 8 + 1.0 * near_self - 1.0 * near_opp

        if opp_t and d_opp <= 1:
            v += 20  # contest close borders

        if v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]