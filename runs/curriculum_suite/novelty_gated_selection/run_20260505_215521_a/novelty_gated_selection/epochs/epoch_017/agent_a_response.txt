def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # If no resources, drift to maximize distance while avoiding obstacles
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            val = (man(nx, ny, ox, oy), -abs(nx - (w-1)/2) - abs(ny - (h-1)/2))
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose a resource where we have advantage vs opponent; favor "high urgency"
    best_t = None
    for rx, ry in resources:
        if not (isinstance(rx, (int, float)) and isinstance(ry, (int, float))):
            continue
        rx = int(rx); ry = int(ry)
        if (rx, ry) in obst:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # positive means we are closer
        advantage = do - ds
        urgency = -ds  # closer is better
        tie = -abs(rx - (w-1)/2) - abs(ry - (h-1)/2)
        val = (advantage, urgency, tie)
        if best_t is None or val > best_t[0]:
            best_t = (val, rx, ry)
    if best_t is None:
        return [0, 0]
    tx, ty = best_t[1], best_t[2]

    # Step toward target with obstacle-aware tie-breaking
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        ds_next = man(nx, ny, tx, ty)
        do_next = man(nx, ny, ox, oy)
        # Prefer reducing distance to target; if blocked, also avoid approaching opponent too much
        val = (-ds_next, -do_next, -man(nx, ny, tx, ty) + man(sx, sy, tx, ty))
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]] if best else [0, 0]