def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick target resource where we have maximal time-advantage; if tie, pick closest.
    best_t = None
    best_key = None
    for tx, ty in resources:
        d_self = man(sx, sy, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        key = (d_opp - d_self, -d_self, -tx, -ty)  # advantage first, then closer, deterministic tie
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer reducing distance to our target; if equal, prefer increasing opponent distance to that same target.
        ns = man(nx, ny, tx, ty)
        no = man(ox, oy, tx, ty)
        key = (-ns, no, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]