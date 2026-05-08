def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources") or []
    targets = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                targets.append((x, y))
        except:
            pass

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if targets:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dto = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
            dpo = abs(nx - ox) + abs(ny - oy)
            sc = -dto - 0.2 * dpo
            if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
                best = (sc, (dx, dy))
        if best is not None:
            return [best[1][0], best[1][1]]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = -(abs(nx - cx) + abs(ny - cy)) - 0.05 * (abs(nx - ox) + abs(ny - oy))
        if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < best[1]):
            best = (sc, (dx, dy))
    if best is not None:
        return [best[1][0], best[1][1]]
    return [0, 0]