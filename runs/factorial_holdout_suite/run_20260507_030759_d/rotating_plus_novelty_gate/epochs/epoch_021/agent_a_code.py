def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If no visible resources, move to deny by maximizing distance from opponent while drifting to center.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = (man(nx, ny, ox, oy),
                 -abs(nx - cx) - abs(ny - cy),
                 -nx, -ny)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # With resources: choose next step that maximizes guaranteed advantage to at least one resource.
    # Primary: (opp_d - self_d) where bigger means we can reach sooner.
    # Secondary: prefer closer self_d among tied advantages; tertiary: drift away from opponent if still tied.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    bestv = None
    res_sorted = sorted((int(r[0]), int(r[1])) for r in resources)
    for dx, dy in sorted(legal, key=lambda t: (t[0], t[1])):
        nx, ny = sx + dx, sy + dy
        best_cell = None
        for rx, ry in res_sorted:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd
            # Encourage taking resources we are strictly closer to; still allow equal if no better.
            v = (adv, -sd, -od, -abs(nx - cx) - abs(ny - cy), -nx, -ny)
            if best_cell is None or v > best_cell:
                best_cell = v
        if best_cell is None:
            continue
        vtop = (best_cell[0], best_cell[1], best_cell[2], best_cell[3], best_cell[4], best_cell[5])
        if bestv is None or vtop > bestv:
            bestv = vtop
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]