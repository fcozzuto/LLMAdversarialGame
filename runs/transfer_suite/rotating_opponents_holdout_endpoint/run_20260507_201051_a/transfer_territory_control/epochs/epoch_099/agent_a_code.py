def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    oppT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_sc = -10**18
    center_x, center_y = w // 2, h // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        # Base: prefer closer to opponent (territory counterclaim game)
        sc = - (abs(nx - ox) + abs(ny - oy)) * 0.6

        # Big incentives
        if (nx, ny) in oppT:
            sc += 50.0 + (abs(nx - sx) + abs(ny - sy)) * -0.01  # enter opponent territory to flip
        elif (nx, ny) in unclaimed:
            sc += 18.0
        elif (nx, ny) in selfT:
            sc += 6.0
        else:
            sc += 0.0

        # Frontier pressure: aim for unclaimed cells adjacent to opponent territory
        adj_opp = 0
        for adx, ady in dirs:
            axx, ayy = nx + adx, ny + ady
            if 0 <= axx < w and 0 <= ayy < h and (axx, ayy) in oppT:
                adj_opp += 1
        sc += adj_opp * 2.5

        # Avoid being trapped: penalize moves with many surrounding obstacles/edges
        blocked = 0
        for adx, ady in dirs:
            axx, ayy = nx + adx, ny + ady
            if not (0 <= axx < w and 0 <= ayy < h) or (axx, ayy) in obst:
                blocked += 1
        sc -= blocked * 0.25

        # Slightly prefer moves that move toward center when not strongly chasing opponent
        sc += (-(abs(nx - center_x) + abs(ny - center_y))) * 0.05

        if sc > best_sc or (sc == best_sc and (dx, dy) == (0, 0)):
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]