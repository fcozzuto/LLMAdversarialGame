def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # Target selection: prioritize resources where we are at least as close as opponent.
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer winning races; then prefer closer ones.
        key = (do - ds, -ds, rx + ry)  # deterministic tie-break by coordinate sum
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    # If no resources, drift toward opponent's corner opposite diagonal.
    if best_target is None:
        tx, ty = (w - 1 if ox < w - 1 else 0), (h - 1 if oy < h - 1 else 0)
    else:
        tx, ty = best_target

    # Move selection: greedily improve toward target while avoiding traps near opponent.
    opp_dist_now = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        # Encourage getting closer to target; discourage getting too close to opponent.
        do = cheb(nx, ny, ox, oy)
        score = (-(ds),  # smaller ds better
                 (do - opp_dist_now),  # prefer increasing distance
                 -abs(nx - tx) - abs(ny - ty),  # secondary
                 0 if (dx == 0 and dy == 0) else 1)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]