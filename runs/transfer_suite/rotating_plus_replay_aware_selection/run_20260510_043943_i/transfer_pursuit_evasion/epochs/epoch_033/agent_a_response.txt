def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = (observation.get("self_role") or "").lower()
    self_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def best_move(target_mode):
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                nx, ny = sx, sy
            if nx == ox and ny == oy:
                score = -10**9 if target_mode == "pursuer" else 10**9
            else:
                d2 = dist2(nx, ny, ox, oy)
                md = abs(nx - ox) + abs(ny - oy)
                if target_mode == "pursuer":
                    # chase tightly; slight bias to reduce max-axis gap and avoid corner-stalling only when needed
                    score = -(d2 * 10 + md)
                else:
                    # evade: maximize distance; also head toward opposite corner relative to opponent
                    cx = 0 if ox > (w - 1) / 2 else (w - 1)
                    cy = 0 if oy > (h - 1) / 2 else (h - 1)
                    dc = dist2(nx, ny, cx, cy)
                    score = (d2 * 10 + dc - md)
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    if self_evader:
        return best_move("evader" if self_evader else "pursuer")
    return best_move("pursuer")