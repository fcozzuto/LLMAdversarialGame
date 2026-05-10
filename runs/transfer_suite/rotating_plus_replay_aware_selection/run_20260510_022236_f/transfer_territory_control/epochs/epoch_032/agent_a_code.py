def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    my_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    cx, cy = (sx, sy)
    if my_terr:
        cx, cy = min(my_terr, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))

    targets = []
    for x, y in (unclaimed | opp_terr):
        if inb(x, y):
            score = (0 if (x, y) in opp_terr else 10) + (abs(x - cx) + abs(y - cy))
            targets.append((score, x, y))
    if not targets:
        for nx in range(sx - 1, sx + 2):
            for ny in range(sy - 1, sy + 2):
                if (nx, ny) != (sx, sy) and inb(nx, ny):
                    return [nx - sx, ny - sy]
        return [0, 0]

    _, tx, ty = min(targets)
    dx = 0 if tx == cx else (1 if tx > cx else -1)
    dy = 0 if ty == cy else (1 if ty > cy else -1)

    for ddx, ddy in [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]:
        nx, ny = cx + ddx, cy + ddy
        if inb(nx, ny):
            return [nx - sx, ny - sy]

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if inb(nx, ny):
            return [ddx, ddy]
    return [0, 0]