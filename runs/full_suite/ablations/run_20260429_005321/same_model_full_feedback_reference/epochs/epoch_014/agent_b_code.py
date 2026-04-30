def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    if not resources:
        # Deterministic drift to improve position relative to opponent
        tx = 0 if ox > (w - 1) // 2 else (w - 1)
        ty = 0 if oy > (h - 1) // 2 else (h - 1)
        best_dxdy = [0, 0]
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            sc = (mdist((nx, ny), (tx, ty)) * 2) - mdist((nx, ny), opp)
            if best is None or sc < best:
                best = sc
                best_dxdy = [dx, dy]
        return best_dxdy

    best_target = None
    best_score = None
    for r in resources:
        d_me = mdist(me, r)
        d_opp = mdist(opp, r)
        # Prefer resources where we are closer; otherwise pick ones that pin opponent far away.
        sc = (d_opp - d_me) * 100 - d_me + (-(abs(r[0] - (w - 1) / 2) + abs(r[1] - (h - 1) / 2))) * 0.01
        if best_score is None or sc > best_score:
            best_score = sc
            best_target = r

    tx, ty = best_target
    best_move = (0, 0)
    best = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d1 = mdist((nx, ny), (tx, ty))
        d2 = mdist((nx, ny), opp)
        # Primary: get closer to target; Secondary: avoid giving opponent too much access.
        sc = d1 * 10 + d1 * (mdist(opp, (tx, ty)) * 0.01) - d2
        if best is None or sc < best:
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]