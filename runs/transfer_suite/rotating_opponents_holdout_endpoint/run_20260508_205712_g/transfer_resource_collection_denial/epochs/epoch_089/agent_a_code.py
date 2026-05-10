def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer resources where we are closer than opponent; otherwise chase nearest.
    best_r = None
    best_key = None
    for r in resources:
        sd = md((sx, sy), r)
        od = md((ox, oy), r)
        adv = od - sd
        key = (adv, -sd, -r[1], -r[0])  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = md((nx, ny), (tx, ty))
        nod = md((ox, oy), (tx, ty))
        n_adv = nod - nsd
        # If multiple moves keep same advantage, go smaller distance to the chosen target.
        k = (n_adv, -nsd, -dy, -dx)
        if best_k is None or k > best_k:
            best_k = k
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]