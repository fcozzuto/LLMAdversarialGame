def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources", None)
    resources = resources if resources else []

    if not resources:
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Race for resources: prefer cells where we are closer than opponent.
        # Key: maximize (do - ds), then minimize ds, then minimize (dist to opponent).
        best_for_cell = None
        for rx, ry in resources:
            if not (isinstance(rx, int) and isinstance(ry, int)):
                continue
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            key = (do - ds, -ds, -dist(nx, ny, ox, oy), -((rx == nx) and (ry == ny)))
            if best_for_cell is None or key > best_for_cell:
                best_for_cell = key

        if best_for_cell is None:
            continue

        if best_key is None or best_for_cell > best_key or (best_for_cell == best_key and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_key = best_for_cell
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]