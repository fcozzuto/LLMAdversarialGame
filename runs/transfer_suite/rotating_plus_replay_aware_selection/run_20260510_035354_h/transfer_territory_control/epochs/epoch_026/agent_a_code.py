def choose_move(observation):
    ax, ay = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 0), observation.get("grid_height", 0)
    opx, opy = observation.get("opponent_position", (0, 0))
    obs_list = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []
    if not w or not h:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    un = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                un.append((x, y))

    if un:
        tx, ty = min(un, key=lambda p: abs(p[0] - ax) + abs(p[1] - ay))
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - opx) + abs(ny - opy)
        sc = -d_t + 0.05 * d_o
        if best is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]