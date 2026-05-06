def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    ox, oy = observation["opponent_position"]
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            resources.append((r[0], r[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in moves if inside(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def md(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    if resources:
        best_val = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dres = min(md(nx, ny, rx, ry) for rx, ry in resources)
            # Prefer smaller distance to resources; tie-break toward staying away from opponent.
            val = (dres, -md(nx, ny, ox, oy), abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)
    else:
        best_val = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # No resources: maximize distance from opponent deterministically.
            val = (-md(nx, ny, ox, oy), abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])]