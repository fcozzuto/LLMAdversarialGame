def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x, y):
        return abs(x - ox) + abs(y - oy)

    self_role = observation.get("self_role", "")
    opponent_role = observation.get("opponent_role", "")
    is_pursuer = ("pursuer" in self_role.lower()) or ("pursuer" in opponent_role.lower() and "evader" in self_role.lower() == False and "evader" not in self_role.lower())

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    dx0 = 0 if ox == sx else (1 if ox > sx else -1)
    dy0 = 0 if oy == sy else (1 if oy > sy else -1)

    pref_orders = []
    pref = (dx0, dy0)
    # Deterministic tie-break: prioritize direction toward/away from opponent.
    for m in moves:
        if m == pref:
            pref_orders.insert(0, m)
        else:
            pref_orders.append(m)
    # If exact pref illegal, keep same order; invalid moves will be filtered.

    if is_pursuer:
        best = None
        best_d = 10**9
        for dx, dy in pref_orders:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = man(nx, ny)
            if d < best_d:
                best_d = d
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    else:
        # Evader: maximize distance; slight bias to keep away diagonally if possible.
        best = None
        best_d = -1
        for dx, dy in pref_orders:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = man(nx, ny)
            if d > best_d:
                best_d = d
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]