def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []) if p)
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if p)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p)
    opp_pos = observation.get("opponent_position", None)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    my_adj = set()
    for (x, y) in selfT:
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                my_adj.add((nx, ny))
    my_adj.add((sx, sy))

    def adj_count(cell, terr):
        x, y = cell
        c = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            if (x + dx, y + dy) in terr:
                c += 1
        return c

    def manh(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in oppT:
            base = 7.0
        elif (nx, ny) in unclaimed:
            base = 9.0
        elif (nx, ny) in selfT:
            base = 2.0
        else:
            base = 0.5
        frontier = 1.5 * adj_count((nx, ny), selfT) + (2.0 if (nx, ny) in my_adj else 0.0)
        risk = 0.0
        if opp_pos is not None:
            od = manh((nx, ny), opp_pos)
            risk -= 0.3 * od
            # If we can take opponent edge cells, prioritize them.
        kill = 0.0
        kill = 2.5 * adj_count((nx, ny), oppT)
        return base + frontier + kill + risk

    best = (0, 0)
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score(nx, ny)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]