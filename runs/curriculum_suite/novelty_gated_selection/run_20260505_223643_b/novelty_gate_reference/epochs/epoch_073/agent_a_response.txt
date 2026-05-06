def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    opp_close_row = 1 if abs(oy - sy) <= 1 else 0

    # Target: maximize distance lead vs opponent; also avoid giving easy row access.
    best = None
    best_key = None
    for rx, ry in resources:
        d_us = man(sx, sy, rx, ry)
        d_opp = man(ox, oy, rx, ry)
        row_pen = 0
        if opp_close_row and abs(ry - oy) <= 1:
            row_pen = 6  # discourage same/easy rows when opponent is near our row band
        if d_us == 0:
            key = (10**9, -0, -rx, -ry)
        else:
            key = ((d_opp - d_us) - row_pen, -d_us, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moves that reduce our distance to target, while increasing distance from opponent.
        s1 = -man(nx, ny, tx, ty)
        s2 = man(nx, ny, ox, oy)
        # Small deterministic tie-break: favor diagonal then right then up
        diag = 1 if dx != 0 and dy != 0 else 0
        tb = (diag, dx, dy)
        score = (s1, s2, tb)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]