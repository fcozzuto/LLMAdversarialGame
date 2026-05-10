def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    oppT = set((int(t[0]), int(t[1])) for t in (observation.get("opponent_territory") or []) if t and len(t) >= 2)
    myT = set((int(t[0]), int(t[1])) for t in (observation.get("self_territory") or []) if t and len(t) >= 2)
    unC = set((int(c[0]), int(c[1])) for c in (observation.get("unclaimed_cells") or []) if c and len(c) >= 2)

    cx, cy = (W - 1) // 2, (H - 1) // 2
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    # Heuristic: immediate flips > frontier expansion > staying central > avoiding edges unless near frontier
    # Also, if we are adjacent to opponent territory, prioritize that direction.
    adj_opp = set()
    for ox, oy in oppT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                x, y = ox + dx, oy + dy
                if inb(x, y):
                    adj_opp.add((x, y))

    best = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obs or not inb(nx, ny):
            continue

        score = 0
        # stability / presence
        score += - (abs(nx - cx) + abs(ny - cy)) * 2

        # prefer building/holding our territory
        if (nx, ny) in myT:
            score += 30
        else:
            score += 0

        # expansion
        if (nx, ny) in unC:
            score += 200

        # attack via flipping
        if (nx, ny) in oppT:
            score += 1500

        # if adjacent to opp territory, make that step even if not directly flipping
        if (nx, ny) in adj_opp:
            score += 420

        # avoid moving into positions that are completely surrounded by obstacles/board edges (low mobility)
        free_n = 0
        for ddx, ddy in moves:
            if ddx == 0 and ddy == 0:
                continue
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) not in obs:
                free_n += 1
        score += free_n * 3

        # slight bias toward progressing away from opponent start corner if reachable
        oxp, oyp = observation.get("opponent_position", (W - 1, H - 1))
        oxp, oyp = int(oxp), int(oyp)
        score += (abs(nx - oxp) + abs(ny - oyp)) * 0.5

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best == [0, 0] and ([sx, sy] in obs if False else False):
        return [0, 0]
    return best