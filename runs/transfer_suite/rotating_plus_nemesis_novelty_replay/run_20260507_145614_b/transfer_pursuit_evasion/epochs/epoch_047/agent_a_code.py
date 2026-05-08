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
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    target_corner = None
    if evader:
        target_corner = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))
    else:
        target_corner = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, target_corner[0], target_corner[1])

        # Secondary term discourages stepping into tight areas: maximize min distance to obstacles.
        # (Deterministic and cheap; helps wall-runner archetype.)
        min_obst = 10**9
        for (px, py) in obst:
            d = dist2(nx, ny, px, py)
            if d < min_obst:
                min_obst = d

        if evader:
            score = (d_opp, min_obst, -d_corner)
        else:
            score = (-d_opp, min_obst, d_corner)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]