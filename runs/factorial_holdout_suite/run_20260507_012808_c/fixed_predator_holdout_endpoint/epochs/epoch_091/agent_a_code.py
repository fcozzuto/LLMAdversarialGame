def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def move_valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a target that we can reach earlier (or at least deny faster).
    best_t = resources[0]
    best_k = None
    for t in resources:
        td = man(t[0], t[1], sx, sy)
        od = man(t[0], t[1], ox, oy)
        # Favor earlier arrival; then maximize denial margin; then prefer closer overall.
        k = (-(td), (od - td), -man(t[0], t[1], w - 1, h - 1), -t[0], -t[1])
        if best_k is None or k > best_k:
            best_k = k
            best_t = t

    tx, ty = best_t

    # Choose the best immediate move by resulting progress/dominance toward the target.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_mv = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not move_valid(nx, ny):
            continue
        nd = man(nx, ny, tx, ty)
        self_d = man(nx, ny, tx, ty)
        opp_d = man(tx, ty, ox, oy)
        # Prefer reducing our distance; also prefer positions that keep us ahead of opponent.
        mv = (-(nd), (opp_d - self_d), -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        if best_mv is None or mv > best_mv:
            best_mv = mv
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]