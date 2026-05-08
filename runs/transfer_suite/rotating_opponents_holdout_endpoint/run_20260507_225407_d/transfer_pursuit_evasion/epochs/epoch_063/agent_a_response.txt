def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("evasion" in r) or ("avoid" in r)

    self_role = observation.get("self_role", "") or ""
    if not is_evader(self_role):
        self_role = observation.get("self_role_name", "") or self_role
    if not is_evader(self_role):
        self_role = observation.get("role", "") or self_role
    evading = is_evader(self_role)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    tx, ty = max(corners, key=lambda c: (abs(c[0] - ox) + abs(c[1] - oy), -c[0], -c[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_tgt = abs(nx - tx) + abs(ny - ty)
        if evading:
            # Escape: maximize distance from pursuer; also converge to the farthest corner
            score = (d_opp, -d_tgt)
        else:
            # Pursue: minimize distance to opponent; also bias toward corner-to-corner pressure
            score = (-d_opp, -d_tgt)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]