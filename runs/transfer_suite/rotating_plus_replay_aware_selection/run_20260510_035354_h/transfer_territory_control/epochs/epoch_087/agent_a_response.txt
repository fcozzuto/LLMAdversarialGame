def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    oppx, oppy = observation.get("opponent_position", (0, 0))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []

    def toset(lst):
        s = set()
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    uset = toset(self_terr)
    oset = toset(opp_terr)
    ucell = toset(unclaimed)
    obset = toset(obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose a deterministic primary goal
    if ucell:
        gx, gy = min(ucell, key=lambda t: abs(t[0] - ax) + abs(t[1] - ay))
    elif oset:
        gx, gy = min(oset, key=lambda t: abs(t[0] - ax) + abs(t[1] - ay))
    else:
        gx, gy = (w // 2, h // 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        dist_goal = abs(nx - gx) + abs(ny - gy)
        dist_opp = abs(nx - oppx) + abs(ny - oppy)
        val = -dist_goal * 25 + dist_opp * 2

        if (nx, ny) in ucell:
            val += 2000
        elif (nx, ny) in oset:
            val -= 500  # avoid stepping into opponent unless forced
        elif (nx, ny) in uset:
            val += 30
        if dx == 0 and dy == 0:
            val -= 10

        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]] if best is not None else [0, 0]