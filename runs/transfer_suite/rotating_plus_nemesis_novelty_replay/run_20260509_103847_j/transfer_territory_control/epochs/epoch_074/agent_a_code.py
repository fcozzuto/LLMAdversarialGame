def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy = int(sx), int(sy)
    ox, oy = int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    candidates = []
    for key in ("unclaimed_cells", "resources"):
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    candidates.append((x, y))
        if candidates:
            break

    if not candidates:
        dxs = (-1, 0, 1)
        best = (10**18, 0, 0)
        for dx in dxs:
            for dy in dxs:
                if abs(dx) + abs(dy) != 1:
                    continue
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny):
                    continue
                d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
                if d > best[0]:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    tx, ty = min(candidates, key=lambda p: (p[0] - sx) * (p[0] - sx) + (p[1] - sy) * (p[1] - sy))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        opp_d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = (d, -opp_d)
        if score < (best[0], best[1]):
            best = (score[0], score[1], dx, dy)
    return [best[2], best[3]]