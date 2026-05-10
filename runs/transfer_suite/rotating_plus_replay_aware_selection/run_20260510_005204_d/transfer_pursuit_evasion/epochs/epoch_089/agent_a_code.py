def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("evade" in role) or ("escape" in role)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_pen(x, y):
        if (x, y) in blocked:
            return 10**9
        p = 0
        for bx, by in blocked:
            d2 = dist2(x, y, bx, by)
            if d2 == 1:
                p += 4
            elif d2 == 2:
                p += 2
        return p

    def free_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_after = dist2(nx, ny, ox, oy)
        pen = obstacle_pen(nx, ny)
        ff = free_count(nx, ny)
        if is_evader:
            score = d_after * 3 + ff * 0.5 - pen
        else:
            score = (-d_after) * 3 + ff * 0.2 - pen
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best