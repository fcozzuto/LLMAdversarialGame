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

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def adj_unclaimed_count(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    c += 1
        return c

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        tx, ty = resources[0]
        best = None
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -manh(nx, ny, tx, ty)
            if (nx, ny) in opp_terr:
                v += 5
            if (nx, ny) in unclaimed:
                v += 2
            v += 0.2 * adj_unclaimed_count(nx, ny)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    best = [0, 0]
    bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        if (nx, ny) in opp_terr:
            v += 10
        elif (nx, ny) in unclaimed:
            v += 6
        elif (nx, ny) in self_terr:
            v += 1
        else:
            v += 0

        v += 0.35 * adj_unclaimed_count(nx, ny)
        v += 0.08 * (-manh(nx, ny, cx, cy))
        v += 0.12 * (-manh(nx, ny, cx, cy))

        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best