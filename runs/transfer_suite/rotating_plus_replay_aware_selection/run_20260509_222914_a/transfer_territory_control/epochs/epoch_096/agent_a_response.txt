def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def adj_unclaimed(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in unclaimed:
                    c += 1
        return c

    def min_obst_dist(x, y):
        if not obstacles:
            return 99
        best = 99
        for ox, oy in obstacles:
            d = abs(ox - x) + abs(oy - y)
            if d < best:
                best = d
        return best

    def dist_to_opp_frontier(x, y):
        if not opp_ter:
            return 999
        bx = by = None
        best = 999
        for ox, oy in opp_ter:
            d = abs(ox - x) + abs(oy - y)
            if d < best:
                best = d
                bx, by = ox, oy
        return best

    best_move = (0, 0)
    best_val = -10**9
    tie = []

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in opp_ter:
            val += 8.0
        elif (nx, ny) in unclaimed:
            val += 3.0
        elif (nx, ny) in self_ter:
            val += 0.5

        val += 0.35 * adj_unclaimed(nx, ny)

        dopp = dist_to_opp_frontier(nx, ny)
        if dopp != 999:
            val += 0.06 * (9 - min(9, dopp))  # mild pull toward opponent territory

        do = min_obst_dist(nx, ny)
        if do <= 1:
            val -= 2.0
        elif do <= 2:
            val -= 0.6
        else:
            val += 0.05

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]