def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    if resources:
        our_t = min(resources, key=lambda r: (manh(sx, sy, r[0], r[1]), r[0], r[1]))
        opp_t = min(resources, key=lambda r: (manh(ox, oy, r[0], r[1]), r[0], r[1]))
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_our = manh(nx, ny, our_t[0], our_t[1])
            d_opp = manh(nx, ny, opp_t[0], opp_t[1])
            d_center = manh(nx, ny, w // 2, h // 2)
            # Primary: reach opponent's nearest resource first; Secondary: keep collecting our closest.
            score1 = d_opp
            score2 = d_our + (0.15 * d_center)
            # Tie-break: prefer moving away from opponent slightly (denial positioning)
            away = manh(nx, ny, ox, oy)
            cand = (score1, score2, -away, moves.index((dx, dy)))
            if cand < best:
                best = cand
        return [best[3] and moves[best[3]][0] or 0, best[3] and moves[best[3]][1] or 0]

    # No resources: drift toward center while keeping distance from opponent.
    cx, cy = w // 2, h // 2
    best = (10**9, -10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_center = manh(nx, ny, cx, cy)
        away = manh(nx, ny, ox, oy)
        cand = (d_center, -away, dx, dy)
        if cand < best:
            best = cand
    return [int(best[2]), int(best[3])]