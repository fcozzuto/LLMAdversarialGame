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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dist_to_obstacles(nx, ny):
        if not obstacles:
            return 99
        best = 99
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    def score_move(nx, ny):
        d = cheb(nx, ny, ox, oy)
        dob = dist_to_obstacles(nx, ny)
        if dob == 0:
            return -10**9 if is_evader else 10**9
        avoid = (6 - dob)  # closer to obstacles is worse
        # Prefer center to reduce corner-trapping and improve mobility.
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center_bias = abs(nx - cx) + abs(ny - cy)

        if is_evader:
            # Maximize distance, then maximize obstacle clearance, then go toward farthest corner-ish (via center_bias).
            return (d * 1000) + (dob * 10) - int(center_bias * 2)
        else:
            # Minimize distance, then maximize obstacle clearance (via negative avoid), then toward center.
            return (-d * 1000) + (dob * 10) - int(center_bias * 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_s = None
    # Deterministic tie-break: fixed dir order; if equal score, pick lexicographically smallest (dx,dy).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        s = score_move(nx, ny)
        if best_s is None or s > best_s:
            best_s = s
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]