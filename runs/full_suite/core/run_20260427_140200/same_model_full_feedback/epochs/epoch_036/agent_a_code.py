def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Fallback: head to the corner opposite opponent while avoiding obstacles
        tx, ty = (0, 0)
        if (ox + oy) <= (w - 1 + h - 1) - (sx + sy):
            tx, ty = (w - 1, h - 1) if (ox < w - 1 or oy < h - 1) else (0, 0)
        best_move = (0, 0)
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = manh(nx, ny, tx, ty) - 0.2 * manh(nx, ny, ox, oy)
            if best_val is None or v < best_val:
                best_val = v
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Primary: greedy toward nearest resource, with small tie-break for staying away from opponent
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        mind = None
        for rx, ry in resources:
            d = manh(nx, ny, rx, ry)
            if mind is None or d < mind:
                mind = d
        # Tie-break: prefer being closer to resources and (slightly) farther from opponent
        v = mind + 0.05 * manh(nx, ny, ox, oy)
        # Deterministic tie-break by move order then coordinates
        if best_val is None or v < best_val:
            best_val = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]