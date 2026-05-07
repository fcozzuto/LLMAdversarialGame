def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set()
    for p in observation.get("obstacles", []):
        obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    move_order = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            move_order.append((dx, dy))

    best = None
    best_move = [0, 0]
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Immediate pickup bonus handled by dominance evaluation via distance=0.
        best_dom = None
        best_our = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            dom = our_d - opp_d  # more negative => we are closer than opponent
            if best_dom is None or dom < best_dom or (dom == best_dom and our_d < best_our):
                best_dom = dom
                best_our = our_d

        # Tie-break: prefer smaller best_dom, then closer to nearest resource overall.
        nearest_our = None
        for rx, ry in resources:
            our_d0 = man(nx, ny, rx, ry)
            if nearest_our is None or our_d0 < nearest_our:
                nearest_our = our_d0
        key = (best_dom, best_our, nearest_our, dx, dy)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return best_move