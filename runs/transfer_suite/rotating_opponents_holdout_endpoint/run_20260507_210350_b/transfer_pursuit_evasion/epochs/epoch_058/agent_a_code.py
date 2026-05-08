def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    self_is_evader = ("evader" in role_self) or ("runner" in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy
    def obs_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    if (sx, sy) in obstacles:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if self_is_evader:
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_tar = dist2(nx, ny, tx, ty)
        p = obs_pen(nx, ny)

        if self_is_evader:
            score = (d_opp, -p, -d_tar)
        else:
            score = (-d_opp, -p, d_tar)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

        if not self_is_evader and d_opp == 0:
            return [dx, dy]

    return [int(best_move[0]), int(best_move[1])]