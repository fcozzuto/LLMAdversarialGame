def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    oxv = ox - sx
    oyv = oy - sy
    # "Perpendicular bias" for evasion: prefer moves that rotate away from direct approach.
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, ox, oy)
        if is_evader:
            # primary: maximize distance; secondary: reduce alignment with opponent (rotate away)
            mvx, mvy = dx, dy
            cross = abs(oxv * mvy - oyv * mvx)
            # Also lightly prefer staying away from immediate corner lock-in
            corner_pen = 0
            if (nx == 0 and ny == 0) or (nx == w - 1 and ny == 0) or (nx == 0 and ny == h - 1) or (nx == w - 1 and ny == h - 1):
                corner_pen = 0.5
            score = (d * 10.0) + cross - corner_pen
            if best is None or score > best_score or (score == best_score and (dx, dy) < best):
                best, best_score = (dx, dy), score
        else:
            # pursuer: minimize distance; secondary: minimize manhattan for quicker capture
            man = abs(nx - ox) + abs(ny - oy)
            score = -(d * 10.0) - man
            if best is None or score > best_score or (score == best_score and (dx, dy) < best):
                best, best_score = (dx, dy), score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]