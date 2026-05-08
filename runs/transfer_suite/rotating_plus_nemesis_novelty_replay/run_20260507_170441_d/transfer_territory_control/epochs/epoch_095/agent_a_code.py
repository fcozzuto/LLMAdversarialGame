def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    unclaimed = observation.get("unclaimed_cells") or []
    targets_src = unclaimed if unclaimed else (observation.get("resources") or [])

    targets = []
    for p in targets_src:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                targets.append((x, y))
        except:
            pass

    if not targets:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    bestv = -10**18
    opp_cell = (ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) == opp_cell:
            v = -10**9
        else:
            dmin = 10**9
            for tx, ty in targets:
                d = abs(tx - nx) + abs(ty - ny)
                if d < dmin:
                    dmin = d
            # Prefer getting closer to nearest target; small bias away from opponent
            v = -dmin * 10 - (abs(nx - ox) + abs(ny - oy))
        if v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]