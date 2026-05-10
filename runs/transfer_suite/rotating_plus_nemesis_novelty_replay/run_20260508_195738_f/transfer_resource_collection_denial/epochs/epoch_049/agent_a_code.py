def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources visible: move to maximize distance from opponent while staying valid
    if not resources:
        best = (None, None)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = (man((nx, ny), (ox, oy)), -man((nx, ny), (0, 0)))
            if best[0] is None or v > best[0]:
                best = (v, (dx, dy))
        return list(best[1]) if best[1] is not None else [0, 0]

    # Choose move that maximizes (opponent disadvantage) for best reachable resource
    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cur_best = None
        for r in resources:
            if (nx, ny) == (r[0], r[1]):
                self_d2 = 0
                opp_d2 = man((ox, oy), r)
            else:
                self_d2 = man((nx, ny), r)
                opp_d2 = man((ox, oy), r)
            # Prefer resources we can reach sooner than opponent; also slightly prefer closeness after advantage
            self_d0 = man((sx, sy), r)
            adv = opp_d2 - self_d2
            v = (adv, -self_d2, -self_d0, -abs(r[0] - ox) - abs(r[1] - oy), -(r[0] * 9 + r[1]))
            if cur_best is None or v > cur_best:
                cur_best = v
        # Secondary tie-break: prevent cornering; prefer moves that reduce distance to some top resource
        overall = (cur_best, -man((nx, ny), (ox, oy)), abs(dx) + abs(dy), -(nx * 9 + ny))
        if best_val is None or overall > best_val:
            best_val = overall
            best_move = (dx, dy)

    return list(best_move) if best_move is not None else [0, 0]