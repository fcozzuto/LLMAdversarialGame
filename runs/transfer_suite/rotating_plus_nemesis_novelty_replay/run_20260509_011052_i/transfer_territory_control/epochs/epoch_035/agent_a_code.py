def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def adj_count(x, y, S):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in S:
                c += 1
        return c

    def man(x, y): return abs(ox - x) + abs(oy - y)

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles: 
            continue

        sc = 0.0
        if (nx, ny) in opp_terr: sc += 7.0
        elif (nx, ny) in unclaimed: sc += 3.5
        elif (nx, ny) in self_terr: sc += 0.6
        else: sc += 0.0

        sc += 0.9 * adj_count(nx, ny, self_terr)
        sc += 0.4 * adj_count(nx, ny, unclaimed)
        sc -= 0.6 * adj_count(nx, ny, opp_terr)

        d = man(nx, ny)
        sc -= 0.05 * d

        if sc > best_sc or (sc == best_sc and [dx, dy] == [0, 0]):
            best_sc = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]