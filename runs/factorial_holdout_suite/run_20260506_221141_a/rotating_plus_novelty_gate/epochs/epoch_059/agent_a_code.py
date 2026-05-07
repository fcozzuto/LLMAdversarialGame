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
    seen = set()
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    if not resources:
        return [0, 0]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        a = dx if dx >= 0 else -dx
        b = dy if dy >= 0 else -dy
        return a if a > b else b

    best_target = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        myd = kdist(sx, sy, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        adv = opd - myd  # positive if we are closer
        # Prefer resources we can reach first; otherwise still pick high adv and closer to us.
        score = adv * 100 - myd * 2
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    tx, ty = best_target
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        # Evaluate by improvement against opponent for the chosen target and safety for future.
        myd = kdist(nx, ny, tx, ty)
        opd = kdist(ox, oy, tx, ty)
        val = (opd - myd) * 100 - myd * 2
        # Mild tie-break: avoid being surrounded by obstacles.
        neigh = 0
        for ax, ay in moves:
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) in blocked:
                neigh += 1
        val -= neigh
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]