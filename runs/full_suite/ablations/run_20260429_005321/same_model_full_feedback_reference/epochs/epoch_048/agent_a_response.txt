def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def choose_target():
        if not resources:
            return None
        best = None
        best_score = None
        # Prefer resources opponent is closer to; otherwise race the nearest.
        for (tx, ty) in resources:
            ds = dist2(sx, sy, tx, ty)
            do = dist2(ox, oy, tx, ty)
            # Score: smaller is better. Huge bonus to deny opponent when they are ahead.
            score = ds
            if do < ds:
                score = ds - 4 * (ds - do)  # become more aggressive
            # Small tie-break to encourage upper-left determinism
            tie = tx * 100 + ty
            score = score + tie * 1e-6
            if best_score is None or score < best_score:
                best_score = score
                best = (tx, ty)
        return best

    target = choose_target()
    if target is None:
        return [0, 0]
    tx, ty = target

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dist2(nx, ny, tx, ty)
        # If opponent is already at/near the same resource, try to drift to reduce their capture likelihood.
        interfere = 0
        if dist2(ox, oy, tx, ty) <= 1:
            # Move away from opponent when they are effectively contesting
            interfere = 0.25 * dist2(nx, ny, ox, oy)
        # Also avoid stepping onto obstacle-adjacent corners by slight preference for staying toward target.
        val = ns - interfere
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]