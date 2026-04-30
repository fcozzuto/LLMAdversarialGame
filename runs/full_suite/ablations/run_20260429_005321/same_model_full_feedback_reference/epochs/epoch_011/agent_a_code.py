def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    oppd_now = md(sx, sy, ox, oy)
    if resources:
        best_target = None
        best_dist = None
        for rx, ry in resources:
            d = md(sx, sy, rx, ry)
            if best_dist is None or d < best_dist or (d == best_dist and (rx, ry) < best_target):
                best_dist = d
                best_target = (rx, ry)
        rx, ry = best_target
        best = None
        best_score = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            d_res = md(nx, ny, rx, ry)
            d_opp = md(nx, ny, ox, oy)
            score = (-d_res) + 0.05 * (d_opp - oppd_now)
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]
    else:
        best = None
        best_score = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            d_opp = md(nx, ny, ox, oy)
            score = (d_opp)  # keep distance when no resources visible
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]