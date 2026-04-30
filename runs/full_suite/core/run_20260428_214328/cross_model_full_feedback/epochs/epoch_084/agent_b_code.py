def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    # unique
    seen = set()
    uniq_resources = []
    for r in resources:
        if r not in seen:
            uniq_resources.append(r)
            seen.add(r)
    resources = uniq_resources

    # helpers
    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    best_move = None
    best_score = -10**9

    # If resources exist, head toward the best resource deterministically
    for r in resources:
        d = cheb((sx, sy), r)
        od = cheb((ox, oy), r)
        score = (od - d) * 10 - d
        if score > best_score:
            best_score = score
            rx, ry = r
            best_move = (rx, ry)

    # If a good resource target found, move towards it
    if best_move is not None:
        dx = rx - sx
        dy = ry - sy
        move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        move_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        nx, ny = sx + move_x, sy + move_y
        if (nx, ny) in obst or not (0 <= nx < w and 0 <= ny < h):
            return [0, 0]
        return [move_x, move_y]

    # Fallback: go toward center if possible, else towards opponent or stay
    center = (w // 2, h // 2)
    dx = center[0] - sx
    dy = center[1] - sy
    move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    move_y = 0 if dy == 0 else (1 if dy > 0 else -1)
    cand = (sx + move_x, sy + move_y)
    if 0 <= cand[0] < w and 0 <= cand[1] < h and cand not in obst:
        return [move_x, move_y]

    # Try moving toward opponent to pressure, else stay
    dx = ox - sx
    dy = oy - sy
    move_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    move_y = 0 if dy == 0 else (1 if dy > 0 else -1)
    cand = (sx + move_x, sy + move_y)
    if 0 <= cand[0] < w and 0 <= cand[1] < h and cand not in obst:
        return [move_x, move_y]

    return [0, 0]