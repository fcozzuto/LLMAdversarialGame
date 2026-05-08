def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    try:
        sx, sy = int(sx), int(sy)
    except:
        sx, sy = 0, 0

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    ox, oy = observation.get("opponent_position", (sx, sy))
    try:
        ox, oy = int(ox), int(oy)
    except:
        ox, oy = sx, sy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = (-(10**18), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            sc = -10**12
        else:
            d_self = abs(nx - sx) + abs(ny - sy)
            d_opp = abs(nx - ox) + abs(ny - oy)
            # deterministic tie-break: earlier dir in dirs list wins due to strict >
            sc = (10**6 if (nx, ny) == (ox, oy) else 0) - d_opp * 10 + (5 if d_self == 1 else -1)
            # slight preference to avoid getting into obstacles' vicinity
            for ddx, ddy in dirs:
                tx, ty = nx + ddx, ny + ddy
                if inb(tx, ty) and (tx, ty) in obstacles:
                    sc -= 3
        if sc > best[0]:
            best = (sc, dx, dy)

    if best[1] == 0 and best[2] == 0 and inb(sx, sy) and (sx, sy) not in obstacles:
        return [0, 0]
    return [int(best[1]), int(best[2])]