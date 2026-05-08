def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    evader = any(k in role for k in ("evader", "escape", "runner", "flee", "evade"))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    nearest_corner = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
    far_corner = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_to_nc = dist2(nx, ny, nearest_corner[0], nearest_corner[1])
        d_to_fc = dist2(nx, ny, far_corner[0], far_corner[1])

        if evader:
            # Keep away from pursuer while drifting toward the farthest corner.
            score = (d_opp) + 0.25 * (d_to_fc) - 0.08 * (d_to_nc)
        else:
            # Pursue by cutting toward the opponent's nearest corner while staying close.
            score = (-d_opp) + 0.55 * (-d_to_nc)

        # Prefer higher score; deterministic tie-break by dx,dy order already fixed.
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]