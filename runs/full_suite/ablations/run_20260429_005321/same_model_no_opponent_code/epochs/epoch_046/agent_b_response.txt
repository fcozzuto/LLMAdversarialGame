def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    if not resources:
        cx, cy = w // 2, h // 2
        tx, ty = cx, cy
        best = (10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2((nx, ny), (tx, ty))
            if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        if best[1] == 0 and best[2] == 0:
            return [0, 0]
        return [best[1], best[2]]

    # Choose target resource favoring ones we are closer to than opponent
    best_t = None
    best_key = None
    for r in resources:
        dS = dist2((sx, sy), r)
        dO = dist2((ox, oy), r)
        # Key: prefer being closer; break ties by proximity and coordinates
        key = (dS - dO, dS, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_t = r

    # One-step lookahead scoring
    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # After moving, choose resource that best exploits advantage
        local_best = None
        local_key = None
        for r in resources:
            dS = dist2((nx, ny), r)
            dO = dist2((ox, oy), r)
            # prefer resources where we gain relative closeness; slight preference for nearer overall
            key = (dS - dO, dS, r[0], r[1])
            if local_key is None or key < local_key:
                local_key = key
                local_best = r
        # Score combines advantage and also avoid moving away from chosen best_t
        adv = local_key[0]
        d_to_t = dist2((nx, ny), best_t)
        score = adv * 1000 + d_to_t
        cand = (score, dx, dy)
        if best_score is None or cand < best:
            best = cand
            best_score = score

    return [int(best[1]), int(best[2])] if best is not None else [0, 0]