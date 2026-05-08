def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    xdir = [-1, 0, 1]
    dirs = [(dx, dy) for dx in xdir for dy in xdir if not (dx == 0 and dy == 0)] + [(0, 0)]

    border = set()
    for tx, ty in opp_terr:
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = tx + dx, ty + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                border.add((nx, ny))

    if border:
        tx, ty = min(border, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
        target = (tx, ty)
    else:
        center = (w // 2, h // 2)
        if unclaimed:
            target = min(unclaimed, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
        else:
            target = center

    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        # Favor stepping onto/near opponent territory; otherwise expand toward target.
        score = 0
        if (nx, ny) in opp_terr:
            score += 1000
        elif (nx, ny) in unclaimed:
            score += 30
        if (nx, ny) in border:
            score += 120
        score += -man(nx, ny, target[0], target[1])
        # Slight preference for moves that move toward the center to avoid getting stuck
        score += -0.01 * man(nx, ny, w // 2, h // 2)
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]