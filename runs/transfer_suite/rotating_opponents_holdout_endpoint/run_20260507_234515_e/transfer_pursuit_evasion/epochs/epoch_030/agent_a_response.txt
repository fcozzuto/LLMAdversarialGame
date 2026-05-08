def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("direct" in role and "evad" not in role) or (not role)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def d2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def free(x, y):
        return inside(x, y) and (x, y) not in oset

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = max(corners, key=lambda c: (c[0] - ox) ** 2 + (c[1] - oy) ** 2) if is_pursuer else \
             max(corners, key=lambda c: (c[0] - sx) ** 2 + (c[1] - sy) ** 2)
    tx, ty = corner

    best = (0, 0)
    bestv = None

    # Deterministic tie-breaking by move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if is_pursuer:
            # Chase opponent; if wall forces detour, prefer reducing distance and increasing local mobility.
            cur = d2(nx, ny)
            mobility = 0
            for mx, my in moves:
                px, py = nx + mx, ny + my
                if free(px, py):
                    mobility += 1
            # Avoid getting stuck: keep some mobility weight.
            v = cur * 10 - mobility
            prefer = "closer"
            key = (v, -mobility, cur)
        else:
            # Evader: maximize distance from pursuer while drifting to a far corner; avoid dead-ends.
            cur = d2(nx, ny)
            mobility = 0
            for mx, my in moves:
                px, py = nx + mx, ny + my
                if free(px, py):
                    mobility += 1
            # Drift to target corner but strongly prioritize staying far.
            corner_d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            v = -cur * 10 + corner_d - mobility  # larger cur, smaller corner_d better, avoid low mobility
            key = (v, -mobility, corner_d)

        if bestv is None or key < bestv:
            bestv = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]