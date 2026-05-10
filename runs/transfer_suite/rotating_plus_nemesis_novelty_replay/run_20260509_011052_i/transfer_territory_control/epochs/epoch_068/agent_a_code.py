def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    px, py = observation.get("opponent_position", (w - 1, h - 1))
    px, py = int(px), int(py)

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = p[0], p[1]
            obs.add((int(x), int(y)))
        except:
            pass

    targets = []
    for p in (observation.get("resources", []) or []):
        try:
            x, y = p[0], p[1]
            targets.append((int(x), int(y)))
        except:
            pass

    unclaimed = []
    for p in (observation.get("unclaimed_cells", []) or []):
        try:
            x, y = p[0], p[1]
            unclaimed.append((int(x), int(y)))
        except:
            pass

    if not targets and unclaimed:
        targets = unclaimed
    if not targets:
        targets = [(px, py)]

    cand = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best_move = (0, 0)
    best_val = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        md = 10**9
        for tx, ty in targets:
            d = abs(tx - nx) + abs(ty - ny)
            if d < md:
                md = d
        if md < best_val:
            best_val = md
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]