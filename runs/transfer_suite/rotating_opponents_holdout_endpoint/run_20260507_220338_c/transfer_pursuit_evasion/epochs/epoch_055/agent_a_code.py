def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role_s = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role_s) or ("avoid" in role_s) or ("runner" in role_s) or ("flee" in role_s)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x, y):
        dx = abs(ox - x); dy = abs(oy - y)
        return dx if dx > dy else dy
    def manh(x, y): return abs(ox - x) + abs(oy - y)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    best_corner = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_score = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        d1 = cheb(nx, ny)
        d2 = manh(nx, ny)
        dcx = best_corner[0] - nx
        dcy = best_corner[1] - ny
        corner = dcx * dcx + dcy * dcy
        cur_d1 = cheb(sx, sy)
        cur_d2 = manh(sx, sy)

        if is_evader:
            score = (d1 * 1000 + d2 * 2 + corner) + (1 if d1 > cur_d1 else 0) + (1 if d2 > cur_d2 else 0)
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)
        else:
            score = (-d1 * 1000 - d2 * 2) + (-1 if d1 > cur_d1 else 0) + (-1 if d2 > cur_d2 else 0)
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]