def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh:
                obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        if isinstance(it, (list, tuple)) and len(it) >= 2:
            x, y = int(it[0]), int(it[1])
            if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def step_cost(x, y, tx, ty):
        return (tx - x) if tx != x else 0, (ty - y) if ty != y else 0

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Choose best resource: maximize lead margin; tie-break by closer to self.
    best = None
    best_key = None
    for tx, ty in resources:
        sd = dist(sx, sy, tx, ty)
        od = dist(ox, oy, tx, ty)
        key = (od - sd, -sd, - (tx + ty) )
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obstacles:
            continue
        sd2 = dist(nx, ny, tx, ty)
        # Prefer moves that improve relative capture race; add slight tie-break to advance.
        od2 = dist(ox, oy, tx, ty)
        v = (od2 - sd2, -sd2, -(nx * 9 + ny))
        if bestv is None or v > bestv:
            bestv = v
            bestm = (dx, dy)

    if bestv is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]