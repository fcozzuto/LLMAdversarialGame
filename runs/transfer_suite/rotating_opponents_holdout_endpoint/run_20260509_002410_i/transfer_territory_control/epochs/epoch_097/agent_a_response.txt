def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    selfT = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unclaimed.add((x, y))

    neigh8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    if not unclaimed and not oppT:
        return [0, 0]

    # Frontier targets: unclaimed cells adjacent to opponent territory; else any unclaimed.
    frontier = []
    if unclaimed and oppT:
        for (x, y) in unclaimed:
            for dx0, dy0 in neigh8:
                if (x + dx0, y + dy0) in oppT:
                    frontier.append((x, y))
                    break
    targets = frontier if frontier else list(unclaimed) if unclaimed else list(oppT)

    ox, oy = int(op[0]), int(op[1])
    best = (0, 0, -10**9)  # (dx, dy, score)

    for dx, dy in neigh8 + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Territory value
        if (nx, ny) in oppT:
            val = 8.0
        elif (nx, ny) in unclaimed:
            val = 4.5
        elif (nx, ny) in selfT:
            val = 1.0
        else:
            val = 0.5

        # Distance pressure: go toward best target, keep away from opponent
        mdist_opp = abs(nx - ox) + abs(ny - oy)
        mdist_target = 10**9
        for tx, ty in targets[:25]:  # deterministic cap
            d = abs(nx - tx) + abs(ny - ty)
            if d < mdist_target:
                mdist_target = d
        score = val * 10.0 + (20.0 - mdist_target) + 0.35 * mdist_opp

        # Prefer not getting stuck on edges behind opponent: slight bias toward reducing dx+dy from opponent corner move
        if (nx == 0 or ny == 0 or nx == w - 1 or ny == h - 1):
            score += 0.15

        if score > best[2]:
            best = (dx, dy, score)

    dx, dy, _ = best
    if (sx + dx, sy + dy) in obstacles:
        return [0, 0]
    return [int(dx), int(dy)]