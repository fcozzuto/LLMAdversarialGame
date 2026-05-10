def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()
    pursuit = ("pursu" in self_role) or ("evad" in opponent_role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def neighbors_open(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = [0, 0]
    best_score = None

    base_d = dist2(sx, sy, ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny, ox, oy)

        open_here = neighbors_open(nx, ny)
        open_opp = neighbors_open(ox, oy)
        corner_target = min([(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)],
                            key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        ck = -abs(nx - corner_target[0]) - abs(ny - corner_target[1])

        if pursuit:
            # Minimize distance to catch; also avoid getting stuck; bias toward corner control.
            score = (base_d - d) * 10.0 + (open_here * 0.3) + (open_opp * -0.05) + (ck * -0.02)
        else:
            # Evade: maximize distance; keep mobility; bias away from opponent's nearest corner.
            score = (d - base_d) * 10.0 + (open_here * 0.4) + (open_opp * 0.05) + (ck * 0.02)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]