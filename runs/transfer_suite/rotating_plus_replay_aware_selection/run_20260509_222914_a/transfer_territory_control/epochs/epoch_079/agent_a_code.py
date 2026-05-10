def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter_list = observation.get("self_territory") or []
    opp_ter_list = observation.get("opponent_territory") or []
    unclaimed_list = observation.get("unclaimed_cells") or []
    obstacles_list = observation.get("obstacles") or []

    self_ter = set((int(p[0]), int(p[1])) for p in self_ter_list if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set((int(p[0]), int(p[1])) for p in opp_ter_list if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in unclaimed_list if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d): 
        dx = a - c
        dy = b - d
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    # Heuristic targets: prefer capturing opponent territory, otherwise take unclaimed adjacent to it.
    opp_targets = list(opp_ter)[:]
    best_opp = None
    best_opp_dist = 10**9
    for tx, ty in opp_targets:
        d = man(sx, sy, tx, ty)
        if d < best_opp_dist:
            best_opp_dist = d
            best_opp = (tx, ty)

    center = (w // 2, h // 2)

    def score_cell(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in self_ter:
            base = 4
        elif (nx, ny) in opp_ter:
            base = 30
        elif (nx, ny) in unclaimed:
            base = 14
        else:
            base = 6  # other territory/unknown

        # Drive toward opponent, but only commit if it increases contest.
        dist_to_opp = man(nx, ny, ox, oy)
        dist_to_center = man(nx, ny, center[0], center[1])
        base += (best_opp_dist if best_opp else 0) * 0.0
        base += max(0, 18 - dist_to_opp) * 1.2
        base += max(0, 10 - dist_to_center) * 0.2

        # If we can flip, strong.
        if (nx, ny) in opp_ter:
            base += 10

        # Prefer unclaimed cells adjacent (8-neighborhood) to opponent territory.
        adj_opp = 0
        for ax, ay in dirs:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in opp_ter:
                adj_opp += 1
        if (nx, ny) in unclaimed:
            base += adj_opp * 5.0

        # Avoid stepping into spots adjacent to obstacles too often.
        adj_obs = 0
        for ax, ay in dirs:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in obstacles:
                adj_obs += 1
        base -= adj_obs * 1.5

        return base

    best_move = [0, 0]
    best_val = score_cell(sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score_cell(nx, ny)
        if v > best_val + 1e-9:
            best_val = v
            best_move = [int(dx), int(dy)]

    return best_move