def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                unclaimed.append((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                opp_terr.add((x, y))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                self_terr.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    if not unclaimed:
        unclaimed = [(ox, oy)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_un = 10**9
        for tx, ty in unclaimed:
            cd = man(nx, ny, tx, ty)
            if cd < d_un:
                d_un = cd

        d_opp = 10**9
        if opp_terr:
            for tx, ty in opp_terr:
                cd = man(nx, ny, tx, ty)
                if cd < d_opp:
                    d_opp = cd
        else:
            d_opp = man(nx, ny, ox, oy)

        # Favor claiming unclaimed quickly, and also approaching opponent-held cells.
        in_opp = (nx, ny) in opp_terr
        in_self = (nx, ny) in self_terr
        score = -d_un + (0.6 if in_opp else 0.0) - 0.15 * d_opp + (0.05 if in_self else 0.0)

        # Deterministic tie-break: prefer moves with smaller dx, then smaller dy, then lexicographically.
        candidates.append((score, dx, dy, nx, ny))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy, _, _ = candidates[0]
    return [int(dx), int(dy)]