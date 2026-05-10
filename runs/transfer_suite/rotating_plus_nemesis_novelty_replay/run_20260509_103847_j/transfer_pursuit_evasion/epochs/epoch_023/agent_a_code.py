def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    role = observation.get("self_role", "pursuer")
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    if role == "evader":
        tx, ty = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        target = (tx, ty)
        want = -1  # minimize distance to target while maximizing distance from opponent
        best_move = (0, 0)
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d_t = dist2(nx, ny, target[0], target[1])
            d_o = dist2(nx, ny, ox, oy)
            score = (d_o, -d_t)
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        target = (ox, oy)
        best_move = (0, 0)
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist2(nx, ny, target[0], target[1])
            score = (-d, -dist2(nx, ny, sx, sy))
            if best_score is None or score > best_score:
                best_score, best_move = score, (dx, dy)
        return [best_move[0], best_move[1]]