def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    opp_set = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    self_set = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    path = observation.get("self_path") or []
    recent = set()
    for p in path[-6:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))
    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    best = None
    best_sc = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            sc = -10**8
        else:
            sc = 0.0
            if (nx, ny) in opp_set:
                sc += 6.0
            elif (nx, ny) in self_set:
                sc += 1.5
            elif (nx, ny) in unclaimed:
                sc += 3.0
            else:
                sc += 0.2

            if (nx, ny) in recent:
                sc -= 1.2

            adj_un = 0; adj_opp = 0
            for adx, ady in dirs[1:]:
                ax, ay = nx + adx, ny + ady
                if not inb(ax, ay) or (ax, ay) in obstacles:
                    continue
                if (ax, ay) in unclaimed:
                    adj_un += 1
                if (ax, ay) in opp_set:
                    adj_opp += 1
            sc += 0.55 * adj_un
            sc -= 0.25 * adj_opp

            ox, oy = map(int, observation["opponent_position"])
            sc -= 0.01 * (abs(nx - ox) + abs(ny - oy))
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best