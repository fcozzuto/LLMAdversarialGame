def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obs = set()
    for b in (observation.get("obstacles", []) or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if inb(x, y):
                obs.add((x, y))

    res = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res0 = res if res else [(sx, sy)]

    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # find nearest resource
        mr2 = min((nx - rx) * (nx - rx) + (ny - ry) * (ny - ry) for rx, ry in res0)
        # avoid moving toward opponent
        dO2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        v = (-mr2) + 0.15 * dO2
        # tiny deterministic tie-breaker
        v2 = v + (dx == 0 and dy == 0) * -0.001 + (dx + 1) * 1e-6 + (dy + 1) * 1e-9

        if bestv is None or v2 > bestv:
            bestv = v2
            best = [dx, dy]

    if best is not None:
        return best
    # fallback: try staying or any valid move
    if inb(sx, sy) and (sx, sy) not in obs:
        return [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]