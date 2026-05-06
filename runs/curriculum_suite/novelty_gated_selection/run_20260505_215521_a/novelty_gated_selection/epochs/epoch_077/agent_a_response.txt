def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # If no resources, move to maximize distance from opponent while avoiding obstacles
    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d = cheb(nx, ny, ox, oy)
            val = d
            if (val, -d, dx, dy) > best:
                best = (val, dx, dy)
        return [best[1], best[2]] if best[0] > -10**8 else [0, 0]

    # Score moves by taking the best resource according to "deny opponent / secure resource"
    # plus small tie-breakers for safety (avoid moving into regions adjacent to obstacles).
    def obstacle_safety(nx, ny):
        s = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obst:
                    s -= 1
        return s

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        self_pos = (nx, ny)
        # Prefer moves that make us closer while keeping opponent further
        best_res = (-10**18, 0)
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Big boost when we can be closer than opponent; deny strongly when opponent is closer.
            rel = od - sd
            # Minor preference: fewer steps for self when parity is close.
            val = rel * 100 + (-sd) + (1 if sd == 0 else 0)
            # Also prefer resources not currently surrounded by obstacles for smoother paths
            val += obstacle_safety(rx, ry) * 2
            if (val, -sd) > best_res:
                best_res = (val, sd)
        move_val = best_res[0] + obstacle_safety(nx, ny)
        if (move_val, -best_res[1], dx, dy) > best:
            best = (move_val, dx, dy)

    return [best[1], best[2]] if best[0] > -10**17 else [0, 0]