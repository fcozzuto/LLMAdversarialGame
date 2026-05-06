def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def step_towards(tx, ty):
        best = (0, 0)
        bestv = -10**9
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -man(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    mx, my = (sx + ox) // 2, (sy + oy) // 2
    best_res = None
    best_val = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds
        # Prefer contestable resources near the "frontier" between agents.
        frontier = -man(mx, my, rx, ry)
        # Slight tie-break to keep movement coherent.
        coherence = -(abs(rx - sx) + abs(ry - sy))
        val = 3 * adv + frontier + 0.1 * coherence
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    rx, ry = best_res
    # If opponent is strictly closer to everything, go to interception point:
    # choose move that minimizes (own distance) to opponent while not moving into dead cells.
    # We detect this by checking maximum achievable advantage.
    max_adv = -10**9
    for r in resources:
        px, py = int(r[0]), int(r[1])
        a = man(ox, oy, px, py) - man(sx, sy, px, py)
        if a > max_adv:
            max_adv = a
    if max_adv < 0:
        best = (0, 0)
        bestv = -10**18
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Prefer reducing opponent's capture edge: minimize do' - ds' (opponent advantage).
            opp_adv = man(nx, ny, ox, oy) - 0  # own distance as proxy for closeness
            # Also steer toward center-frontier to potentially steal later.
            frontier = -man(mx, my, nx, ny)
            v = 5 * opp_adv + 0.5 * frontier
            # Deterministic tie-break: prefer non-staying.
            if v > bestv or (v == bestv and (dx != 0 or dy != 0)):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    return step_towards(rx, ry)