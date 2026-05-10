def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    self_terr = set((p[0], p[1]) for p in observation.get("self_territory") or [])
    opp_terr = set((p[0], p[1]) for p in observation.get("opponent_territory") or [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles") or [])
    unclaimed = set((p[0], p[1]) for p in observation.get("unclaimed_cells") or [])

    cx = ox
    cy = oy
    if opp_terr:
        sx2 = 0
        sy2 = 0
        n = 0
        for px, py in opp_terr:
            sx2 += px
            sy2 += py
            n += 1
        cx = sx2 // n
        cy = sy2 // n

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors_free(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                c += 1
        return c

    def adj_to_our(x, y):
        c = 0
        for dx, dy in dirs4:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self_terr:
                c += 1
        return c

    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_terr:
            base = 1.0
        elif (nx, ny) in opp_terr:
            base = 10.0
        elif (nx, ny) in unclaimed:
            base = 6.0
        else:
            base = 2.0

        d_opp = abs(nx - cx) + abs(ny - cy)
        d_opp_cur = abs(sx - cx) + abs(sy - cy)
        approach = (d_opp_cur - d_opp)

        mobility = neighbors_free(nx, ny)
        edge_guard = adj_to_our(nx, ny)

        val = base + 0.8 * approach + 0.5 * edge_guard + 0.2 * mobility
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best == [0, 0]:
        for dx, dy in dirs8:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles and not (nx, ny) in self_terr:
                best = [dx, dy]
                break
    return [int(best[0]), int(best[1])]