def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)

    obstacles = set()
    for x, y in (observation.get("obstacles") or []):
        if x is not None and y is not None:
            obstacles.add((int(x), int(y)))

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs8 = moves

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_to_nearest_opp(x, y):
        if not opp_t:
            return 999
        md = 999
        for ox, oy in opp_t:
            d = abs(x - ox) + abs(y - oy)
            if d < md:
                md = d
        return md

    def adj_self(x, y):
        for dx, dy in dirs8:
            if (x + dx, y + dy) in self_t:
                return True
        return False

    best = [0, 0]
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        s = 0
        if (nx, ny) in opp_t:
            s += 12
        elif (nx, ny) in unclaimed:
            s += 6
        else:
            s += 1 if (nx, ny) in self_t else 0

        if adj_self(nx, ny):
            s += 3

        dopp = dist_to_nearest_opp(nx, ny)
        s -= 2 * dopp

        if nx == sx and ny == sy:
            s -= 0.5

        # slight bias toward advancing from corner diagonally to reach center
        center_bias = 0.03 * (abs((w - 1) / 2 - sy) - abs((w - 1) / 2 - ny))
        s += center_bias

        if s > best_score or (s == best_score and (dx, dy) < tuple(best)):
            best_score = s
            best = [dx, dy]

    return best if inb(sx + best[0], sy + best[1]) and (sx + best[0], sy + best[1]) not in obstacles else [0, 0]