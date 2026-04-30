def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def safe_moves_from(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny):
                out.append((dx, dy))
        return out if out else [(0, 0)]

    # If no resources visible, try to approach opponent's side to contest unseen resources
    if not resources:
        tx, ty = ox, oy
        best = (0, 0)
        bestv = None
        for dx, dy in safe_moves_from(sx, sy):
            nx, ny = sx + dx, sy + dy
            v = dist2(nx, ny, tx, ty)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Score candidate resources by advantage: (opp_dist - my_dist); prefer larger advantage, then closer to me
    sorted_res = sorted(
        resources,
        key=lambda r: (
            -(dist2(ox, oy, r[0], r[1]) - dist2(sx, sy, r[0], r[1])),
            dist2(sx, sy, r[0], r[1]),
            r[0],
            r[1],
        ),
    )

    # Evaluate only top few targets for speed/robustness
    top_targets = sorted_res[:min(6, len(sorted_res))]

    best_move = (0, 0)
    best_val = None
    for dx, dy in safe_moves_from(sx, sy):
        nx, ny = sx + dx, sy + dy
        # Prefer moving to targets where we reduce the opponent-relative gap most
        val = 0
        for j, (rx, ry) in enumerate(top_targets):
            myd = dist2(nx, ny, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            myd0 = dist2(sx, sy, rx, ry)
            opd0 = dist2(ox, oy, rx, ry)
            # gain in relative advantage
            gain = (opd - myd) - (opd0 - myd0)
            # encourage actual approach and immediate picking
            val += (gain * 100) + (-myd) + (-j * 5)
        # small bias: stay nearer to current target direction, avoid standing still if possible
        if (dx, dy) == (0, 0):
            val -= 2
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]