def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            rr = (int(r[0]), int(r[1]))
            if rr not in obstacles:
                resources.append(rr)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def min_dist_from(px, py):
        best = 10**9
        for rx, ry in resources:
            d = md(px, py, rx, ry)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    opp_candidates = []
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if inb(nx, ny):
            opp_candidates.append((dx, dy, nx, ny))

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_d = min_dist_from(nx, ny)

        opp_best = 10**9
        for _, _, px, py in opp_candidates:
            d = min_dist_from(px, py)
            if d < opp_best:
                opp_best = d
                if opp_best == 0:
                    break

        diag_pref = 1 if dx != 0 and dy != 0 else 0
        key = (opp_best - my_d, -my_d, diag_pref, -abs(dx) - abs(dy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]