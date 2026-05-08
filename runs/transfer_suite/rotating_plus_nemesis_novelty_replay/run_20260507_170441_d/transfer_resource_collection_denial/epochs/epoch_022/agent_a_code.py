def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Greedy target selection per candidate move with "exclusive resource" priority.
    best = (10**9, 10**9, -10**9, 0, 0)  # (self_dist, opp_dist, -margin, dx, dy) lower better
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        exclusive = []
        best_any = None
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            margin = oppd - selfd
            if margin >= 2:
                exclusive.append((selfd, oppd, -margin, rx, ry))
            else:
                # Track best "race" target as fallback: closest self; tie by largest margin.
                key = (selfd, -margin, oppd)
                if best_any is None or key < best_any[0]:
                    best_any = (key, selfd, oppd, -margin, rx, ry)

        if exclusive:
            # Prefer closest among exclusive resources; tie by opponent distance (closer opponent later is better) then by margin.
            exclusive.sort(key=lambda t: (t[0], t[1], t[2]))
            selfd, oppd, negm, _, _ = exclusive[0]
            margin = -negm
        else:
            selfd = best_any[1]
            oppd = best_any[2]
            margin = best_any[3]

        # Evaluate move: minimize our distance; if tied minimize opponent distance; maximize margin.
        tup = (selfd, oppd, -margin, dx, dy)
        if tup < best:
            best = tup

    return [best[3], best[4]]