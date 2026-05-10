def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    self_is_evader = any(k in role for k in ("evader", "evade", "runner", "escape", "coward"))
    opp_is_evader = not self_is_evader

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    target_corner = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy)) if opp_is_evader else max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_opp = cheb(nx, ny, ox, oy)
        d_to_corner = cheb(nx, ny, target_corner[0], target_corner[1])
        if self_is_evader:
            # Escape: maximize distance to pursuer, drift to target corner.
            val = (-d_to_opp) + 0.35 * d_to_corner
            # actually we want larger d_to_opp => smaller negative; and smaller d_to_corner
            # convert to "minimize": val = -d_to_opp + 0.35*d_to_corner
        else:
            # Pursue: minimize distance to evader, also approach likely corner target.
            val = d_to_opp - 0.15 * (7 - d_to_corner)  # prefer smaller corner distance
        if best is None or val < best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best