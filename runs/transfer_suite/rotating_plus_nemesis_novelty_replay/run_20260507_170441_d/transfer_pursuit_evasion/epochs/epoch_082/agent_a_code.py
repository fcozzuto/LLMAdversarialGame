def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = None
    best_corner_score = None
    for cx, cy in corners:
        if not free(cx, cy):
            continue
        d = abs(cx - ox) + abs(cy - oy)
        if is_evader:
            score = d
            if best_corner_score is None or score > best_corner_score:
                best_corner_score = score
                target_corner = (cx, cy)
        else:
            score = -d
            if best_corner_score is None or score > best_corner_score:
                best_corner_score = score
                target_corner = (cx, cy)
    if target_corner is None:
        target_corner = (0, 0)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = None
    cx, cy = target_corner
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        d_corner = man(nx, ny, cx, cy)
        # Primary: distance to opponent (maximize if evader, minimize if pursuer)
        if is_evader:
            score = d_opp * 1000 + d_corner
        else:
            score = -d_opp * 1000 - d_corner
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best