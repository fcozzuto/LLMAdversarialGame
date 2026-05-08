def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break bias by turn_index
    phase = int(observation.get("turn_index", 0) or 0) % 9
    ordered = moves[phase:] + moves[:phase]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbor_open(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if ok(nx, ny):
                c += 1
        return c

    best = None
    best_val = -10**18
    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            continue  # avoid immediate capture
        ddx, ddy = nx - ox, ny - oy
        dist = ddx * ddx + ddy * ddy  # maximize distance
        open_nei = neighbor_open(nx, ny)  # prefer escape routes
        # also avoid stepping adjacent to opponent too closely
        man = abs(nx - ox) + abs(ny - oy)
        val = dist * 10 + open_nei * 3 - (0 if man >= 3 else (6 - man) * 8)
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        # fallback: stay put
        return [0, 0]
    return best