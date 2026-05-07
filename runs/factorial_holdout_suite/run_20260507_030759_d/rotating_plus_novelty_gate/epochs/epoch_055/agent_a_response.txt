def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # Move to increase distance from opponent while staying safe
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            cand = (-manh(nx, ny, ox, oy), dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    # Score each neighbor by best contested resource
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue
        local_best = None
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; also prefer closer pickups
            score = (od - sd) * 10 - sd
            # Small tie-break to reduce chasing far resources when contest is equal
            score2 = -manh(nx, ny, ox, oy)
            cand = (-score, -score2, sd, od, rx, ry)
            if local_best is None or cand < local_best:
                local_best = cand
        if local_best is None:
            continue
        # Prefer diagonal-free deterministic tie-break via dx,dy order embedded
        outer = (local_best[0], local_best[1], local_best[2], local_best[3], local_best[4], local_best[5], dx, dy)
        if best is None or outer < best:
            best = outer

    return [best[-2], best[-1]]