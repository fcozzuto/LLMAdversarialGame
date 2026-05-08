def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))
    moves.append((0, 0))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    unclaimed_list = list(unclaimed)[:18]
    unclaimed_list.sort(key=lambda p: (p[0], p[1]))

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in oppT:
            val += 120.0
        elif (nx, ny) in unclaimed:
            val += 25.0
        elif (nx, ny) not in selfT and (nx, ny) not in oppT:
            val += 12.0
        else:
            val += 2.0

        val += -0.12 * man(nx, ny, cx, cy)
        val += 0.06 * (man(nx, ny, ox, oy) * -1.0)  # prefer closer to opponent
        if unclaimed_list:
            dmin = 10**9
            for ux, uy in unclaimed_list:
                d = man(nx, ny, ux, uy)
                if d < dmin:
                    dmin = d
            val += -0.20 * dmin

        if val > best_val:
            best_val = val
            best = [dx, dy]
        elif val == best_val:
            if best is None or (dx, dy) < (best[0], best[1]):
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]