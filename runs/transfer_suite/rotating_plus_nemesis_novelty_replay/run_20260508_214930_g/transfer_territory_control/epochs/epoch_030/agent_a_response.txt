def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    def any_adj(x, y, sset):
        for nx, ny in adj8(x, y):
            if (nx, ny) in sset:
                return True
        return False

    def count_adj(x, y, sset):
        c = 0
        for nx, ny in adj8(x, y):
            if (nx, ny) in sset:
                c += 1
        return c

    # Deterministic preference: capture opponent if adjacent; otherwise expand into unclaimed
    opp_adj_here = any_adj(sx, sy, opp_t)
    best = (0, 0)
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        v = 0
        if (nx, ny) in opp_t:
            v += 500 + 40 * count_adj(nx, ny, self_t) - 20 * count_adj(nx, ny, opp_t)
            if opp_adj_here:
                v += 80  # keep pressure if currently in the duel zone
        elif (nx, ny) in unclaimed:
            v += 120
            v += 25 * count_adj(nx, ny, self_t)  # grow from our boundary
            v -= 25 * count_adj(nx, ny, opp_t)   # avoid giving them adjacency leverage
            v -= 2 * (abs(nx - sx) + abs(ny - sy))
        elif (nx, ny) in self_t:
            v += 10
            v += 10 * count_adj(nx, ny, self_t)
            v -= 18 * count_adj(nx, ny, opp_t)
            v -= 1 * (abs(nx - sx) + abs(ny - sy))
        else:
            v -= 5

        # Mild tendency to push away from local opponent proximity
        min_opp_d = 10
        for ox, oy in (observation.get("opponent_territory") or []):
            d = abs(ox - nx) + abs(oy - ny)
            if d < min_opp_d:
                min_opp_d = d
                if min_opp_d <= 1:
                    break
        v += 3 * min_opp_d
        if dx == 0 and dy == 0:
            v -= 6 if not opp_adj_here else 0

        # Deterministic tie-break: fixed dir order already; only replace if strictly better
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]