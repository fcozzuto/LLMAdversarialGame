def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None
    best_key = None

    for dx, dy, nx, ny in moves:
        # Greedy 1-step lookahead: pick the resource we'd be best positioned to contest from (nx, ny).
        best_adv = -10**9
        best_md = 10**9
        best_rx, best_ry = nx, ny
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            if adv > best_adv or (adv == best_adv and self_d < best_md):
                best_adv = adv
                best_md = self_d
                best_rx, best_ry = rx, ry
        # Extra deterministic bias: prefer moving in a direction that increases distance from opponent
        # when advantages tie (helps against edge patrol).
        opp_dist_now = man(nx, ny, ox, oy)
        opp_dist_prev = man(sx, sy, ox, oy)
        delta_opp = opp_dist_now - opp_dist_prev

        key = (best_adv, delta_opp, -best_md, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]