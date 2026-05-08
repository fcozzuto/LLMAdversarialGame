def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = max(abs(nx - tx), abs(ny - ty))
            cand = (d, abs(nx - sx) + abs(ny - sy), dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[2], best[3]] if best is not None else [0, 0]

    def cd(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        local_best = None
        for rx, ry in resources:
            ds = cd(nx, ny, rx, ry)
            do = cd(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; otherwise prefer reducing opponent advantage.
            # Deterministic tie-breaking via ordered tuple.
            key = (ds > do, -(do - ds), ds, do, rx, ry)
            if local_best is None or key < local_best:
                local_best = key
        # Secondary: keep moves that improve our distance to the selected target.
        key2 = (local_best, abs(dx) + abs(dy), dx, dy, nx, ny)
        if best_key is None or key2 < best_key:
            best_key = key2
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]