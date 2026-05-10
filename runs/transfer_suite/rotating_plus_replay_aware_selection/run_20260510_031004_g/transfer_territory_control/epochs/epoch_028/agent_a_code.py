def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def adj_opp(x, y):
        return max(abs(x - px), abs(y - py)) == 1

    def count_adj_unclaimed(x, y):
        cnt = 0
        for ddx, ddy in dirs:
            nx, ny = x + ddx, y + ddy
            if (nx, ny) in unclaimed:
                cnt += 1
        return cnt

    best = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        is_un = (nx, ny) in unclaimed
        is_self = (nx, ny) in self_terr
        is_opp = (nx, ny) in opp_terr

        if is_un:
            val += 260
            val += 18 * count_adj_unclaimed(nx, ny)
        if is_self:
            val += 22
        if is_opp:
            val += 1200
            val += 80 * count_adj_unclaimed(nx, ny)

        # Tactical: if adjacent to opponent, prefer moves that can steal/claim frontier cells
        if adj_opp(nx, ny):
            if is_opp:
                val += 140
            elif is_un:
                val += 90
            else:
                val -= 40

        # Avoid getting too close unless stealing
        d = max(abs(nx - px), abs(ny - py))
        if d <= 1 and not is_opp:
            val -= 120
        elif d <= 2 and not is_opp:
            val -= 35

        # One-step lookahead to prefer routes toward nearby unclaimed
        look = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if not free(tx, ty):
                continue
            if (tx, ty) in unclaimed:
                look = max(look, 25 - dist2(tx, ty, px, py) // 10)
            if (tx, ty) in opp_terr:
                look = max(look, 300)
        val += look

        # Deterministic tie-breaker: closer to unclaimed if values equal-ish
        val += -(dist2(nx, ny, px, py) // 50)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]