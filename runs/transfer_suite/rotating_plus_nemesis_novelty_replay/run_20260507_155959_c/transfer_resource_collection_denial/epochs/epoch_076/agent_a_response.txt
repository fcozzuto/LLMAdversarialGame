def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                valid_moves.append((dx, dy))
    valid_moves.append((0, 0))
    valid_moves = sorted(set(valid_moves))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in valid_moves:
            nx, ny = sx + dx, sy + dy
            k = (md(nx, ny, tx, ty), abs(dx) + abs(dy), dx, dy)
            if best is None or k < best[0]:
                best = (k, (dx, dy))
        return [best[1][0], best[1][1]]

    # Race strategy: prefer resources where we are closer than opponent.
    best_t = None
    for p in resources:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        tx, ty = p[0], p[1]
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        sd = md(sx, sy, tx, ty)
        od = md(ox, oy, tx, ty)
        # Higher advantage first; then closer self; then deterministic position order.
        k = (od - sd, -sd, -tx, -ty, tx, ty)
        if best_t is None or k > best_t[0]:
            best_t = (k, (tx, ty))

    tx, ty = best_t[1]
    # Choose best feasible neighbor step toward the chosen resource.
    best = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        k = (md(nx, ny, tx, ty), abs(dx) + abs(dy), dx, dy)
        if best is None or k < best[0]:
            best = (k, (dx, dy))
    return [best[1][0], best[1][1]]