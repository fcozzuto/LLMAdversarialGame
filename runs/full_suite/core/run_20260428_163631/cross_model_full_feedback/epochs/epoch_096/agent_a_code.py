def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)
    center = (w // 2, h // 2)

    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if (dx, dy) not in legal:
            continue
        nm = (nx, ny)

        if resources:
            dres = [man(nm, r) for r in resources]
            min_d = min(dres)
            min_idx = dres.index(min_d)
            target = resources[min_idx]
            res_bonus = 0
            if nm == target:
                res_bonus = 1000
            # Prefer moving to reduce distance to the nearest resource
            progress = man(me, target) - man(nm, target)
            # Avoid getting too close to opponent unless we're on a resource
            adj = max(abs(nx - ox), abs(ny - oy))
            opp_pen = 0
            if adj <= 1:
                opp_pen = 25 if res_bonus == 0 else -5
            if adj == 0:
                opp_pen += 40
            val = (-(min_d * 10) + progress * 15 + res_bonus) - opp_pen
        else:
            # No resources visible: drift toward center but keep away from opponent
            min_d = man(nm, center)
            adj = max(abs(nx - ox), abs(ny - oy))
            val = -(min_d * 8) - (30 if adj <= 1 else 0)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]