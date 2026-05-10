def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("catch" in role) or ("pred" in role) or (observation.get("environment_name", "") == "pursuit_evasion" and "evader" not in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def min_obst_d(x, y):
        if not obstacles:
            return 7
        md = 99
        for bx, by in obstacles:
            d = abs(x - bx) + abs(y - by)
            if d < md:
                md = d
                if md <= 0:
                    break
        return 7 if md == 99 else md

    def clamp_pos(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = clamp_pos(sx + dx, sy + dy)
        if (nx, ny) in obstacles and (nx, ny) != (sx, sy):
            continue
        d = mdist(nx, ny, ox, oy)
        od = min_obst_d(nx, ny)
        boundary_pen = 0
        if nx != sx + dx: boundary_pen += 1.0
        if ny != sy + dy: boundary_pen += 1.0
        if pursuer:
            score = (-d) + (0.18 * od) - (0.35 * boundary_pen)
        else:
            score = (d) + (0.18 * od) - (0.35 * boundary_pen)
        if best is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]