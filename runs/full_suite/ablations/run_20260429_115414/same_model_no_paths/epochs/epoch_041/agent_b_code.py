def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if free(rx, ry):
                resources.append((rx, ry))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        bestd = None
        for rx, ry in resources:
            d = abs(rx - sx)
            e = abs(ry - sy)
            dist = d if d > e else e
            if best is None or dist < bestd or (dist == bestd and (rx, ry) < best):
                best = (rx, ry)
                bestd = dist
        rx, ry = best
        stepx = 0 if rx == sx else (1 if rx > sx else -1)
        stepy = 0 if ry == sy else (1 if ry > sy else -1)

        cand = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0 and stepx == 0 and stepy == 0:
                    pass
                nx, ny = sx + dx, sy + dy
                if free(nx, ny):
                    cand.append((dx, dy))
        if not cand:
            return [0, 0]

        cand.sort(key=lambda t: (-(t[0] == stepx) - (t[1] == stepy), abs((sx + t[0]) - rx) + abs((sy + t[1]) - ry), (t[0], t[1])))
        return [int(cand[0][0]), int(cand[0][1])]

    # No resources: move toward opponent if possible, otherwise stay or pick first free neighbor
    dxop = 0 if ox == sx else (1 if ox > sx else -1)
    dyop = 0 if oy == sy else (1 if oy > sy else -1)
    for dx, dy in [(dxop, dyop), (dxop, 0), (0, dyop), (0, 0)]:
        if free(sx + dx, sy + dy):
            return [int(dx), int(dy)]

    for dx, dy in dirs:
        if free(sx + dx, sy + dy):
            return [int(dx), int(dy)]
    return [0, 0]