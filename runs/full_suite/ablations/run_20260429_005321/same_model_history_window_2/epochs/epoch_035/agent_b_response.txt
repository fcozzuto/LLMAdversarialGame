def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def best_target_score(px, py):
        if not resources:
            return None, -10**9
        best = None
        best_sc = -10**9
        for tx, ty in resources:
            d_self = dist(px, py, tx, ty)
            d_opp = dist(ox, oy, tx, ty)
            sc = (d_opp - d_self) * 100 - d_self  # win race first, then be closer
            if (tx, ty) == (px, py):
                sc += 10**6
            if sc > best_sc or (sc == best_sc and (tx, ty) < best):
                best_sc = sc
                best = (tx, ty)
        return best, best_sc

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        _, sc = best_target_score(nx, ny)
        candidates.append((sc, nx, ny, dx, dy))

    # Prefer moves that also increase our advantage; deterministic tie-break by position and move delta
    candidates.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
    return [int(candidates[0][3]), int(candidates[0][4])]