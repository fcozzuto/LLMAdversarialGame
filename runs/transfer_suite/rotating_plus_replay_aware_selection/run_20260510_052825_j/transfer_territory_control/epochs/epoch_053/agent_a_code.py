def choose_move(observation):
    w = observation.get("grid_width", 1)
    h = observation.get("grid_height", 1)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    resources = list(map(tuple, observation.get("resources") or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if unclaimed:
        # Prefer cells closer to us than to opponent, then by distance from opponent, then by coordinates.
        best_cell = None
        best_key = None
        for cx, cy in unclaimed:
            if (cx, cy) in obstacles or not inb(cx, cy):
                continue
            ds = man(cx, cy, x, y)
            do = man(cx, cy, ox, oy)
            key = (0 if ds <= do else 1, do, ds, cx, cy)
            if best_key is None or key < best_key:
                best_key = key
                best_cell = (cx, cy)
        tx, ty = best_cell if best_cell is not None else (ox, oy)
    elif resources:
        rx, ry = min(resources, key=lambda p: (man(p[0], p[1], ox, oy), man(p[0], p[1], x, y), p[0], p[1]))
        tx, ty = rx, ry
    else:
        # No targets known: move away from opponent.
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_target = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        # Maximize: farther from opponent, closer to target (or away if target is opponent).
        score = (d_opp, -d_target, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]