def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_list = list(opp_terr)
    neigh8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    frontier = []
    if opp_list:
        for ox, oy in opp_list:
            for dx, dy in neigh8:
                nx, ny = ox + dx, oy + dy
                if (nx, ny) in unclaimed:
                    frontier.append((nx, ny))
    frontier = list(dict.fromkeys(frontier))

    if frontier:
        tx, ty = min(frontier, key=lambda c: (man((sx, sy), c), man((int(cx), int(cy)), c)))
    else:
        best_un = list(unclaimed)
        if best_un:
            tx, ty = min(best_un, key=lambda c: (man((sx, sy), c), -((c[0]-cx)*(c[0]-cx)+(c[1]-cy)*(c[1]-cy))))
        else:
            tx, ty = int(cx), int(cy)

    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0
        cell = (nx, ny)
        score = 0.0
        if cell in opp_terr:
            score += 9.0
        if cell in unclaimed:
            score += 3.2
        if cell in self_terr:
            score -= 0.2
        score += 2.0 / (1 + man(cell, (tx, ty)))
        score += -0.08 * ((cell[0] - cx) ** 2 + (cell[1] - cy) ** 2)
        if (dx, dy, score) > best:
            best = (dx, dy, score)

    return [best[0], best[1]]