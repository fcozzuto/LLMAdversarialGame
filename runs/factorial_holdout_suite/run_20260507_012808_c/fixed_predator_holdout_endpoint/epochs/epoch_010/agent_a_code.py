def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources", []) or []
    res = resources[:]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []) if len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid_moves():
        ms = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    ms.append((dx, dy))
        if ms:
            return ms
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    ms.append((dx, dy))
        return ms if ms else [(0, 0)]

    moves = valid_moves()

    if res:
        tx, ty = min(res, key=lambda r: (man(sx, sy, r[0], r[1]), r[0], r[1]))
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            dres = man(nx, ny, tx, ty)
            dmid = man(nx, ny, ox, oy)
            # Prefer reducing distance to target, while keeping some distance from opponent
            v = (dres, -dmid, abs(dx) + abs(dy), dx, dy)
            if best is None or v < bestv:
                best, bestv = (dx, dy), v
        return [best[0], best[1]]

    # No resources: move to increase distance from opponent
    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        dv = (-man(nx, ny, ox, oy), abs(dx) + abs(dy), dx, dy)
        if best is None or dv < bestv:
            best, bestv = (dx, dy), dv
    return [best[0], best[1]]