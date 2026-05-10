def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources_xy = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources_xy.append((rx, ry))
    if not resources_xy:
        return [0, 0]

    def best_for_self(px, py):
        best = None
        best_key = None
        for tx, ty in resources_xy:
            ds = man(px, py, tx, ty)
            do = man(ox, oy, tx, ty)
            key = (ds - do, ds, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty, ds, do)
        return best

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        tx, ty, ds, do = best_for_self(nx, ny)
        # Prefer increasing our relative advantage; then closeness; then tie-break deterministically by move.
        val = (do - ds, -ds, tx, ty, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]