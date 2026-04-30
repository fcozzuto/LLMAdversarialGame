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
    seen = set()
    uniq_resources = []
    for r in resources:
        if r not in seen:
            uniq_resources.append(r)
            seen.add(r)
    resources = uniq_resources

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
            dx = 0
            dy = 0
            if rx > sx: dx = 1
            elif rx < sx: dx = -1
            else: dx = 0
            if ry > sy: dy = 1
            elif ry < sy: dy = -1
            else: dy = 0
            best_move = [dx, dy]

    if best_move is not None:
        # ensure legal
        nx, ny = sx + best_move[0], sy + best_move[1]
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return best_move

    # Fallback: move toward opponent to interfere, deterministic
    dx = 0
    dy = 0
    if ox > sx: dx = 1
    elif ox < sx: dx = -1
    if oy > sy: dy = 1
    elif oy < sy: dy = -1
    if dx != 0 or dy != 0:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [dx, dy]

    # If blocked, try any valid step that stays in bounds
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                return [dx, dy]

    # As last resort stay
    return [0, 0]