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

    def kdist(a, b, c, d):
        dx, dy = a - c, b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Choose best target resource by "race advantage", then best immediate move toward it.
    best_target = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        # Prefer places we can reach sooner; break ties deterministically.
        val = (od - sd) * 100 - sd * 2 + (-rx) * 0.01 + (ry) * 0.001
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in blocked:
            nx, ny = sx, sy
        # Evaluate: how much closer we become vs opponent, after taking this step.
        sd2 = kdist(nx, ny, tx, ty)
        od2 = kdist(ox, oy, tx, ty)
        score = (od2 - sd2) * 100 - sd2 * 2
        # Secondary: avoid steps that increase distance to the globally best target set.
        if score > best_score:
            best_score = score
            best_move = [int(nx - sx), int(ny - sy)]

    return best_move