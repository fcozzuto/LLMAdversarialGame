def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        dx = -dx if dx < 0 else dx
        dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # Precompute a weak "center of mass" to reduce dithering.
    cx = cy = 0
    n = len(resources)
    for rx, ry in resources:
        cx += rx
        cy += ry
    cx = cx // n
    cy = cy // n

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy

        my_to_center = kdist(nx, ny, cx, cy)
        # Maximize: advantage in reaching any resource + slight preference for being closer to center.
        val = -my_to_center * 0.05
        for rx, ry in resources:
            md = kdist(nx, ny, rx, ry)
            od = kdist(ox, oy, rx, ry)
            # Primary: prefer resources where we can arrive sooner than opponent.
            # Secondary: tie-break by being closer overall.
            cand = (od - md) * 10.0 - md * 0.2
            if cand > val:
                val = cand

        # Deterministic tie-break: prefer moves with smaller |dx|+|dy|, then lexicographic.
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            cur = abs(best_move[0]) + abs(best_move[1])
            new = abs(dx) + abs(dy)
            if new < cur or (new == cur and (dx, dy) < (best_move[0], best_move[1])):
                best_move = [dx, dy]

    return best_move