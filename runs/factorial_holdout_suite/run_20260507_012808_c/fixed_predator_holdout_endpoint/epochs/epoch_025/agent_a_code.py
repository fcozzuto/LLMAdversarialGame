def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    legal.append((0, 0))

    if resources:
        best = None
        bestv = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles:
                continue
            mind = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if d < mind:
                    mind = d
            v = -mind - 0.01 * (abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            best = (0, 0)
        return [int(best[0]), int(best[1])]

    # No visible resources: maximize distance from opponent to avoid capture/trap
    best = (0, 0)
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        v = abs(nx - ox) + abs(ny - oy)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]