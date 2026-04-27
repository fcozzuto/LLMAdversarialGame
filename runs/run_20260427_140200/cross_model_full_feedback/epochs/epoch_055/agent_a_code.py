def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = (w - 1) - ox, (h - 1) - oy
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = -cheb(nx, ny, tx, ty)
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    # Deterministic priority: maximize (reachability advantage on closest contestable resource) + avoid opponent
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        my_min = 10**9
        opp_min = 10**9
        nearest = (nx, ny)
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            dom = cheb(ox, oy, rx, ry)
            # if opponent can already be significantly closer, deprioritize; otherwise take advantage
            if dme < my_min:
                my_min = dme
                nearest = (rx, ry)
            if dom < opp_min:
                opp_min = dom

        rx, ry = nearest
        dme0 = cheb(nx, ny, rx, ry)
        dom0 = cheb(ox, oy, rx, ry)

        # Reward closer to a target resource; penalize being closer to opponent (prevents contested interception)
        opp_d = cheb(nx, ny, ox, oy)
        if opp_d == 0:
            val = -10**12
        else:
            contest_adv = dom0 - dme0  # positive means we are closer than opponent to this chosen resource
            # Encourage reaching before opponent, but still move even if opponent is closer by taking some progress.
            val = 1000 * contest_adv - 10 * dme0 + 6 * (opp_d - 1)
            # Small tie-breaker towards staying near the map center early/overall
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val -= 0.01 * (abs(nx - cx) + abs(ny - cy))

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]