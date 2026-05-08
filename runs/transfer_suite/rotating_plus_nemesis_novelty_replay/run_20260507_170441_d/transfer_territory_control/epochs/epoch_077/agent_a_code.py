def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w); h = int(h)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    blocked = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                targets.append((x, y))
        except:
            pass

    if targets:
        tx, ty = min(targets, key=lambda t: (t[0]-sx)*(t[0]-sx) + (t[1]-sy)*(t[1]-sy))
    else:
        tx, ty = (w // 2, h // 2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in blocked:
            continue
        d_t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        d_o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        v = (-d_t) + (2 * d_o)
        if best is None or v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]