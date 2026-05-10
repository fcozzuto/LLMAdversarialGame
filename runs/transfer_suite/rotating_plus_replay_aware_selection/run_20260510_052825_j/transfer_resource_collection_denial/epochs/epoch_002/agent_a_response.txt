def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (sd - 0.9 * od, sd, od, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        rx, ry = resources[0][0], resources[0][1]
    else:
        rx, ry = best[1]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur_sd = cheb(sx, sy, rx, ry)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ns = cheb(nx, ny, rx, ry)
        no = cheb(ox, oy, rx, ry)
        adv = no - cheb(ox, oy, nx, ny)
        candidates.append((ns - 0.6 * no, ns, -adv, dx, dy))
    if not candidates:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            ns = cheb(nx, ny, rx, ry)
            no = cheb(ox, oy, rx, ry)
            adv = no - cheb(ox, oy, nx, ny)
            candidates.append((ns - 0.6 * no, ns, -adv, dx, dy))

    candidates.sort()
    chosen = candidates[0]
    return [chosen[3], chosen[4]]