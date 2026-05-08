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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    def score(nx, ny):
        d = cheb(nx, ny)
        if is_evader:
            return (d, -abs(nx - sx) - abs(ny - sy))
        else:
            return (-d, -abs(nx - sx) - abs(ny - sy))

    candidates = []
    deltas = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    base_phase = int(observation.get("turn_index", 0) or 0) % 4
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        corner_bonus = 0
        if is_evader:
            tx, ty = corners[(base_phase + i) % 4]
            corner_bonus = abs(tx - nx) + abs(ty - ny)
            return_score = (score(nx, ny)[0] * 100 + corner_bonus,)
        else:
            return_score = (score(nx, ny)[0] * 100 + cheb(nx, ny),)
        candidates.append((return_score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0][0], -t[0][1] if len(t[0]) > 1 else 0, t[1], t[2]))
    best = candidates[-1]
    return [int(best[1]), int(best[2])]