def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except:
            pass

    targets = observation.get("unclaimed_cells", None)
    if targets is None:
        targets = observation.get("resources", None)
    targets = targets or []

    tlist = []
    for p in targets:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                tlist.append((x, y))
        except:
            pass
    if not tlist:
        tlist = [(ox, oy)]

    best_move = (0, 0)
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue
            tx, ty = min(tlist, key=lambda q: (q[0] - nx) * (q[0] - nx) + (q[1] - ny) * (q[1] - ny))
            d2 = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            block = -0.01 * ((ox - nx) * (ox - nx) + (oy - ny) * (oy - ny))
            val = -d2 + block
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]