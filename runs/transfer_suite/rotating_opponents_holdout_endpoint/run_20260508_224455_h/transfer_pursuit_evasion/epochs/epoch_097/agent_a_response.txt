def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return (dx if dx >= 0 else -dx) if (abs(dx) >= abs(dy)) else (dy if dy >= 0 else -dy)

    want_evade = (role == "evader" or role == "evading" or role == "runner")
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        d = cheb(nx, ny, ox, oy)
        # Tie-break toward moves that avoid staying still when possible.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        # Evader maximizes distance; pursuer minimizes.
        val = d - 0.01 * stay_pen if want_evade else -d - 0.01 * stay_pen
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]