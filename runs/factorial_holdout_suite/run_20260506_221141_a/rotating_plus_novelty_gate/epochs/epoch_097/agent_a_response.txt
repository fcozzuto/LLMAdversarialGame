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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = resources[0]
    best_key = None
    for rx, ry in sorted(resources):
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        # Prefer winning the race; then maximize lead; then prefer nearer; then deterministic by coords
        key = (0 if sd == 0 else 1, sd <= od, sd - od, -od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if (sx, sy) == (tx, ty):
        return [0, 0]

    deltas = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                deltas.append((dx, dy))

    # Deterministic order + score: minimize distance to target, avoid losing the race when possible
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nsd = kdist(nx, ny, tx, ty)
        nod = kdist(ox, oy, tx, ty)
        score = (nsd, nod - nsd, 0 if (dx, dy) == (0, 0) else 1, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]