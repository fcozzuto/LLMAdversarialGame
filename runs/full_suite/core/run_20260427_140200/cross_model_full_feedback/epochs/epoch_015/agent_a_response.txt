def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in candidates:
            d = abs(nx - tx) + abs(ny - ty)
            # deterministic tiebreak: prefer away from opponent slightly
            t = (d, -(abs(nx - ox) + abs(ny - oy)), dx, dy)
            if best is None or t < best[0]:
                best = (t, [dx, dy])
        return best[1]

    best_move = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        d_me_opp = abs(nx - ox) + abs(ny - oy)
        best_val = -10**18
        for rx, ry in resources:
            d_me = abs(nx - rx) + abs(ny - ry)
            d_opp = abs(ox - rx) + abs(oy - ry)
            # Encourage going to resources where we are relatively closer; strongly avoid letting opponent be much closer.
            rel = d_opp - d_me  # positive if I'm closer
            val = (rel * 6) - (d_me * 1.2)
            if (nx == rx and ny == ry):
                val += 50
            if val > best_val:
                best_val = val
        # secondary criteria: contest opponent proximity only when values are close
        key = (-best_val, d_me_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move