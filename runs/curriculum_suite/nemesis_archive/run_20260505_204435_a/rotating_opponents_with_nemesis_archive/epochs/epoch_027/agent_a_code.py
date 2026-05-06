def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                x, y = pos[0], pos[1]
                if legal(x, y):
                    resources.append((x, y))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if legal(x, y):
                resources.append((x, y))

    if not legal(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        # Choose move that minimizes Manhattan distance to nearest resource.
        best = (10**9, 10**9, 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            dmin = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            # Tie-breaks: prefer not moving into worse position vs opponent.
            do = abs(nx - ox) + abs(ny - oy)
            key = (dmin, do, -abs(dx) - abs(dy), dx, dy)
            if key < best[:5]:
                best = (key[0], key[1], key[2], dx, dy)
        return [best[3], best[4]]

    # No resources: deterministically move toward opponent.
    tx, ty = ox, oy
    bestd = 10**9
    bestm = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        if d < bestd:
            bestd = d
            bestm = [dx, dy]
    return bestm