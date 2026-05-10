def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("escape" in role) or ("runner" in role) or ("hider" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    gx = 0 if ox == sx else (1 if ox > sx else -1)
    gy = 0 if oy == sy else (1 if oy > sy else -1)

    best_dxdy = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)

        # Prefer moves that continue the chase direction; avoid "side-stepping" into walls.
        dev = abs(dx - gx) + abs(dy - gy)
        edge_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_pen = 3

        # If pursuer: minimize distance strongly, then minimize deviation/edge penalty.
        # If evader: maximize distance strongly, then maximize deviation from chase direction, and avoid edges slightly.
        if evader:
            score = (-d * 1000) + (dev * 10) - edge_pen
            better = (best_score is None) or (score > best_score)
        else:
            score = (d * 1000) + (dev * 10) + edge_pen
            better = (best_score is None) or (score < best_score)

        if better:
            best_score = score
            best_dxdy = (dx, dy)

    dx, dy = best_dxdy
    return [int(dx), int(dy)]