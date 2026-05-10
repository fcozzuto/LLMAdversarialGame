def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_terr = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.add((int(p[0]), int(p[1])))

    resources = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x, y, x2, y2):
        return abs(x - x2) + abs(y - y2)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_key = None

    target_resources = resources if resources else set()
    target_unclaimed = unclaimed if unclaimed else set()

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in opp_terr:
            penalty = 100000
        else:
            penalty = 0

        if target_resources:
            dist = min(man(nx, ny, rx, ry) for (rx, ry) in target_resources)
            in_res = 1 if (nx, ny) in target_resources else 0
            key = (-(in_res), dist, penalty, 0 if (nx, ny) in self_terr else 1, man(nx, ny, ox, oy))
        else:
            in_uc = 1 if (nx, ny) in target_unclaimed else 0
            dist_opp = man(nx, ny, ox, oy)
            key = (-(in_uc), penalty, 0 if (nx, ny) in self_terr else 1, -dist_opp, man(nx, ny, sx, sy))

        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best