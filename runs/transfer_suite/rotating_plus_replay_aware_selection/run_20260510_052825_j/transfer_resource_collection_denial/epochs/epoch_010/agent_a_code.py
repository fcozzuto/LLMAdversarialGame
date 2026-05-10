def choose_move(observation):
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get('obstacles', []) or []))
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        v = ax - bx
        if v < 0:
            v = -v
        u = ay - by
        if u < 0:
            u = -u
        return v + u

    best = None
    best_dxdy = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        best_margin = -10**9
        best_self_d = 10**9

        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            margin = od - sd  # positive => we are closer
            if margin > best_margin or (margin == best_margin and sd < best_self_d):
                best_margin = margin
                best_self_d = sd

        # Prefer winning race to a resource; if all races are bad, move toward nearest resource.
        val = best_margin * 1000 - best_self_d
        if best is None or val > best or (val == best and (dx, dy) < best_dxdy):
            best = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]