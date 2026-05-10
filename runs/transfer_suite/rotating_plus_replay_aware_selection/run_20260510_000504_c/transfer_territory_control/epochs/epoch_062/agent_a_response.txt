def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    resources = observation.get("resources") or []
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if resources:
        tx, ty = resources[0]
        best = list(resources)[0]
    else:
        # Prefer a frontier: unclaimed adjacent to our territory
        frontier = []
        if self_terr:
            for (x, y) in self_terr:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                            frontier.append((nx, ny))
        targets = frontier or list(unclaimed) or list(opp_terr)
        if not targets:
            targets = [(int(cx), int(cy))]
        # Deterministic: closest, then closer to center, then y,x
        best = targets[0]
        bx, by = best
        bestkey = (dist(sx, sy, bx, by), dist(bx, by, cx, cy), by, bx)
        for (x, y) in targets:
            key = (dist(sx, sy, x, y), dist(x, y, cx, cy), y, x)
            if key < bestkey:
                bestkey = key
                best = (x, y)
        tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            cell = (nx, ny)
            # Priority: capture unclaimed > flip opponent > stay/other
            if cell in unclaimed:
                pr = 3
            elif cell in opp_terr:
                pr = 2
            elif cell in self_terr:
                pr = 1
            else:
                pr = 0
            d = dist(nx, ny, tx, ty)
            cen = -dist(nx, ny, cx, cy)
            moves.append(( -pr, d, -cen, ny, nx, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    return [int(moves[0][5]), int(moves[0][6])]