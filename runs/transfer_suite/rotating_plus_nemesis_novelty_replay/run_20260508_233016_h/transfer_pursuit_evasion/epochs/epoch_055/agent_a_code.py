def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Choose a primary target deterministically
    if resources:
        # Prefer nearest resource; tie-break by lexicographic position
        target = min(resources, key=lambda t: (dist2(sx, sy, t[0], t[1]), t[0], t[1]))
        tx, ty = target
    else:
        tx, ty = ox, oy

    best = None
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dres = dist2(nx, ny, tx, ty)
        dop = dist2(nx, ny, ox, oy)

        # If opponent is very close, keep some distance; otherwise, aim for resource/target
        close_pen = 0
        if dop <= 4:
            close_pen = 50 - dop  # larger penalty when closer

        # Small deterministic bias to reduce oscillation: prefer non-zero move if tied
        bias = 0.01 * (abs(dx) + abs(dy))

        val = -dres - close_pen + bias
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        # Fallback: stay if stuck
        return [0, 0]
    return best