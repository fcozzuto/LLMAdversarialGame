def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        cells = []
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                if inb(rx, ry):
                    cells.append((rx, ry))
        if not cells:
            cells = None

        if cells:
            best_move = (0, 0)
            best_score = -10**18
            for dx, dy in deltas:
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny):
                    continue
                dist_opp = md(nx, ny, ox, oy)
                best_margin = -10**18
                best_myd = 10**9
                for rx, ry in cells:
                    myd = md(nx, ny, rx, ry)
                    opd = md(ox, oy, rx, ry)
                    margin = opd - myd
                    if margin > best_margin or (margin == best_margin and myd < best_myd):
                        best_margin = margin
                        best_myd = myd
                score = best_margin * 10 - best_myd - dist_opp // 4
                if score > best_score:
                    best_score = score
                    best_move = (dx, dy)
            return [best_move[0], best_move[1]]

    # Fallback: head to center while staying away from opponent
    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist_center = md(nx, ny, cx, cy)
        dist_opp = md(nx, ny, ox, oy)
        score = dist_opp * 2 - dist_center
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]