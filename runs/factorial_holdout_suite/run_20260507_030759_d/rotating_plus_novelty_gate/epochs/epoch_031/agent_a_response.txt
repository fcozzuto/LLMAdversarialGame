def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            lead = do - ds  # positive if we are closer
            # Prefer resources we can reach first; tie-break by absolute lead then by our distance
            key = (lead, -ds, -abs(rx - ox) - abs(ry - oy), rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
        # If already on a resource, stay unless blocked (handled by legality)
        if (sx, sy) == (tx, ty):
            return [0, 0]

        # Greedy step: among legal moves, pick the one that decreases our manhattan to target,
        # and also increases chance we stay ahead of opponent (using next-step distances)
        scored = []
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            ns = abs(tx - nx) + abs(ty - ny)
            no = abs(tx - ox) + abs(ty - oy)
            lead = no - ns
            # Higher lead first, then smaller ns, then prefer moves that reduce both coords toward target
            score = (lead, -ns, -(abs(tx - nx) + abs(ty - ny)), -abs(ox - nx) - abs(oy - ny), dx, dy)
            scored.append((score, dx, dy))
        scored.sort(reverse=True)
        return [scored[0][1], scored[0][2]]

    # No resources: move to corner farthest from opponent while avoiding obstacles
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best_corner = None
    best_val = None
    for cx, cy in corners:
        if (cx, cy) in obstacles:
            continue
        val = (abs(cx - ox) + abs(cy - oy), -abs(cx - sx) - abs(cy - sy), cx, cy)
        if best_val is None or val > best_val:
            best_val = val
            best_corner = (cx, cy)
    cx, cy = best_corner if best_corner is not None else (0, 0)

    # Step toward chosen corner with obstacle-aware legal move selection
    scored = []
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist = abs(cx - nx) + abs(cy - ny)
        opp_dist = abs(cx - ox) + abs(cy - oy)
        score = (opp_dist - (abs(cx - nx) + abs(cy - ny)), -dist, -abs(cx - ox) - abs(cy - oy), dx, dy)
        scored.append((score, dx, dy))
    scored.sort(reverse=True)
    return [scored[0][1], scored[0][2]]