def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in ob
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                res.append((rx, ry))
    if not res:
        # deterministic center drift
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    # opponent's likely target: nearest resource to opponent
    opp_target = None
    best_od = 10**9
    for rx, ry in res:
        d = md(ox, oy, rx, ry)
        if d < best_od:
            best_od = d
            opp_target = (rx, ry)

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        # race score: after this move, maximize advantage on any resource
        # advantage = (opp_dist - self_dist). Prefer also reducing self_dist to that resource.
        sc = -10**18
        if opp_target is not None:
            tx, ty = opp_target
            sc += 0.15 * (md(ox, oy, tx, ty) - md(nx, ny, tx, ty))  # small focus on opp target

        max_adv = -10**9
        best_self_d = 10**9
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            if adv > max_adv or (adv == max_adv and sd < best_self_d):
                max_adv = adv
                best_self_d = sd
        sc += 1.0 * max_adv - 0.05 * best_self_d

        # if we cannot get advantage, drift toward center to improve future control
        if max_adv <= 0:
            sc -= 0.02 * (md(nx, ny, cx, cy))

        # deterministic tie-break: prefer larger x then y deltas to keep stable
        key = (sc, dx, dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]