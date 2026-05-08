def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    role = (observation.get("self_role") or "").lower()
    is_pursuer = any(k in role for k in ("purs", "hunt", "chaser", "seeker", "hunter", "pursuer", "catch"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def best_pursuer():
        # Greedy chase with small preference to avoid getting stuck near obstacles
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            # obstacle adjacency penalty
            pen = 0
            for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (nx + ax, ny + ay) in obstacles:
                    pen += 1
            score = d + pen * 0.25
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return best[1] if best else [0, 0]

    def best_evader():
        # Escape to the farthest accessible corner; if all blocked, maximize distance directly.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        best_corner = None
        for cx, cy in corners:
            if (cx, cy) in obstacles:
                continue
            d = dist2(cx, cy, ox, oy)
            if best_corner is None or d > best_corner[0] or (d == best_corner[0] and (cx, cy) < best_corner[1]):
                best_corner = (d, (cx, cy))
        target = best_corner[1] if best_corner else (0, 0)

        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_to_opp = dist2(nx, ny, ox, oy)
            d_to_target = dist2(nx, ny, target[0], target[1])
            # Prefer increasing distance to opponent; then move toward chosen corner
            score = (-d_to_opp) + d_to_target * 0.01
            if best is None or score < best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return best[1] if best else [0, 0]

    return list(best_pursuer() if is_pursuer else best_evader())