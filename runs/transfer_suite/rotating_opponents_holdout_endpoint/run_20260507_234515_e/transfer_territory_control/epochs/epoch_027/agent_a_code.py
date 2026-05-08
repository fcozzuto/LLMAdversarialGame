def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1), (0, 0)]

    border = set()
    for tx, ty in opp_terr:
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = tx + dx, ty + dy
            if inside(nx, ny) and (nx, ny) not in obstacles and (nx, ny) not in opp_terr:
                border.add((nx, ny))

    target = None
    if border:
        target = min(border, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
    elif unclaimed:
        target = min(unclaimed, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        if opp_terr:
            focus = min(opp_terr, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))
            target = focus
        else:
            return [0, 0]

    tx, ty = target
    if (sx, sy) == (tx, ty):
        return [0, 0]

    best_step = (0, 0)
    best_cost = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        cost = man(nx, ny, tx, ty)
        if (nx, ny) in opp_terr:
            cost -= 1  # prefer stepping into opponent territory to flip
        if (nx, ny) in self_terr:
            cost += 0.2  # slight disincentive
        if cost < best_cost or (cost == best_cost and (dx, dy) < best_step):
            best_cost = cost
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]