def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    dirs = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def neigh_count(x, y, terrset):
        c = 0
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and not blocked(nx, ny) and (nx, ny) in terrset:
                c += 1
        return c

    best = (None, -10**9, 10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            val = -10**8
        else:
            val = 0
            if (nx, ny) in unclaimed:
                val += 100
            elif (nx, ny) in opp_terr:
                val += 60
            elif (nx, ny) in self_terr:
                val += 15
            else:
                val += 5
            val += 6 * neigh_count(nx, ny, opp_terr)
            val += 2 * neigh_count(nx, ny, self_terr)
            # Prefer moving towards center to form/maintain territory
            dcenter = abs(nx - cx) + abs(ny - cy)
            val -= int(dcenter * 2)
            # Mild anti-loop: slightly prefer cells with fewer adjacent self cells
            val -= 2 * neigh_count(nx, ny, self_terr)
        dcent2 = abs((sx + dx) - cx) + abs((sy + dy) - cy)
        # fixed tie-breaker by move order (dirs list order)
        if val > best[1] or (val == best[1] and dcent2 < best[2]):
            best = ((dx, dy), val, dcent2)

    return [int(best[0][0]), int(best[0][1])]