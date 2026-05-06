def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            continue

        my = (nx, ny)
        total = 0.0

        for i in range(len(resources)):
            rx, ry = resources[i]
            r = (rx, ry)
            myd = dist(my, r)
            opd = dist((ox, oy), r)
            # Positive means we are closer than opponent to that resource.
            # Bias toward immediate captures and toward resources where we create lead.
            lead = (opd - myd)
            total += (2.5 if myd == 0 else 0.0) + (lead * 1.2) - (0.08 * myd)

        # Extra pressure: if we can improve our overall advantage over the closest resource, prefer it.
        # (Keeps deterministic "interceptor" flavor without full pathfinding.)
        closest = min(resources, key=lambda r: dist((nx, ny), r))
        myc = dist((nx, ny), closest)
        opc = dist((ox, oy), closest)
        total += (opc - myc) * 0.9

        if best_val is None or total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]