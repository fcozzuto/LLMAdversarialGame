def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Precompute frontier adjacency to reward expansion/entry into opponent space
    def adj_opp_or_unclaimed(x, y):
        c = 0
        for dx, dy in dirs8:
            nx, ny = x + dx, y + dy
            if (nx, ny) in opp_terr or (nx, ny) in unclaimed:
                c += 1
        return c

    best = None
    best_val = None
    order = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # invalid => stay
        # cell type
        if (nx, ny) in opp_terr:
            type_score = 120
        elif (nx, ny) in unclaimed:
            type_score = 55
        elif (nx, ny) in self_terr:
            type_score = 5
        else:
            type_score = 10
        # arrival advantage for this step target
        d_self = abs(nx - sx) + abs(ny - sy)  # mostly 0/1; keeps greedy stable
        d_opp = abs(nx - ox) + abs(ny - oy)
        advantage = d_opp - (0 if d_self <= 0 else 1)
        # push toward center for stable control
        center = -(abs(nx - cx) + abs(ny - cy))
        # expansion pressure
        frontier = adj_opp_or_unclaimed(nx, ny) * 8
        val = type_score + advantage * 10 + frontier + center
        if best is None or val > best_val:
            best, best_val = (dx, dy), val
    return [int(best[0]), int(best[1])]