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

    # Pick target resource by deterministic advantage against opponent
    best = None
    best_key = None
    for rx, ry in sorted(resources):
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        # Prefer winning race; then maximize opponent disadvantage; then smaller distance; then determinism
        key = (1 if sd <= od else 0, od - sd, -sd, -(rx + ry), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        # Evaluate immediate step toward target and how it affects race
        nd = kdist(nx, ny, tx, ty)
        opd = kdist(ox, oy, tx, ty)
        adv = opd - nd
        # Small bias to progress in x/y to break ties deterministically
        key = (1 if nd <= opd else 0, adv, -nd, -abs(tx - nx) - abs(ty - ny), -dx, -dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move