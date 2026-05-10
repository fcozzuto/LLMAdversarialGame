def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    oppT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    cx = (w - 1) // 2
    cy = (h - 1) // 2

    candidates = []
    for dx, dy in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in oppT:
            pr = 30
        elif (nx, ny) in unclaimed:
            pr = 20
        elif (nx, ny) in selfT:
            pr = 10
        else:
            pr = 15

        free_nbrs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                xx, yy = nx + ddx, ny + ddy
                if inb(xx, yy) and (xx, yy) not in obstacles:
                    free_nbrs += 1

        if oppT:
            d_to_opp = min(man(nx, ny, ox, oy) for ox, oy in oppT)
        else:
            d_to_opp = 99

        d_to_center = man(nx, ny, cx, cy)

        candidates.append((pr, free_nbrs, -d_to_opp, -d_to_center, dx, dy))

    if not candidates:
        return [0, 0]
    best = max(candidates)
    return [int(best[4]), int(best[5])]