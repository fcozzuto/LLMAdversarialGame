def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    try:
        sx, sy = int(sp[0]), int(sp[1])
    except:
        sx, sy = 0, 0
    try:
        ox, oy = int(op[0]), int(op[1])
    except:
        ox, oy = 0, 0

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            try:
                bx, by = int(b[0]), int(b[1])
            except:
                continue
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or role.endswith("e")

    resources = observation.get("resources", None)
    res_list = []
    if isinstance(resources, (list, tuple)):
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                try:
                    rx, ry = int(r[0]), int(r[1])
                except:
                    continue
                if 0 <= rx < w and 0 <= ry < h:
                    res_list.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0: d1 = -d1
        d2 = ay - by
        if d2 < 0: d2 = -d2
        return d1 + d2

    best = None
    best_score = -10**18
    fallback = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        if fallback == [0, 0]:
            fallback = [dx, dy]

        mind_res = None
        if res_list:
            dmin = 10**9
            for rx, ry in res_list:
                d = dist(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
            mind_res = dmin

        d_opp = dist(nx, ny, ox, oy)

        if is_evader:
            score = d_opp
            if mind_res is not None:
                score += max(0, 50 - mind_res)
        else:
            score = -d_opp
            if mind_res is not None:
                score += max(0, 50 - mind_res)

        score += (0.01 * (nx - sx) + 0.001 * (ny - sy))
        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is None:
        nx, ny = sx, sy
        if safe(nx, ny):
            return [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if safe(nx, ny):
                return [dx, dy]
        return [0, 0]
    return best