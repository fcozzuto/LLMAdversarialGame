def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_key = None

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            md = None
            do = None
            for rx, ry in resources:
                d = abs(nx - rx) + abs(ny - ry)
                if md is None or d < md:
                    md = d
                od = abs(ox - rx) + abs(oy - ry)
                if do is None or od < do:
                    do = od
            # Prefer closer to nearest resource; break ties by also considering opponent distance.
            key = (md, -(do if do is not None else 0), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (abs(nx - cx) + abs(ny - cy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best