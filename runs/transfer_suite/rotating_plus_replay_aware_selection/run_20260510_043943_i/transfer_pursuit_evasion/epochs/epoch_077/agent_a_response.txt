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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_move(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return False
        return (nx, ny) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick target corner deterministically to improve corner evasion.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    corner = corners[0]
    best_corner_score = -1
    for c in corners:
        cx, cy = c
        if cheb(cx, cy, ox, oy) > best_corner_score:
            corner = c
            best_corner_score = cheb(cx, cy, ox, oy)
    tx, ty = corner

    best = None
    best_val = None  # higher for evader, lower for pursuer
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not clamp_move(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        # If near opponent, evader prioritizes immediate distance gain; pursuer prioritizes immediate reduction.
        # Also use target corner for evader to break symmetry deterministically.
        if is_evader:
            corner_dist = cheb(nx, ny, tx, ty)
            val = (d_opp * 1000) + corner_dist
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        else:
            val = d_opp * 1000 - (0)  # keep simple, obstacle-safe greedy chase
            if best_val is None or val < best_val:
                best_val = val
                best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]