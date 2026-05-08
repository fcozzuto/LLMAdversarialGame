def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = []
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs.append((int(x), int(y)))
        except Exception:
            pass
    obs_set = set(obs)

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role) or ("evasion" in role) or role == "evader"

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obs_set

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = md(nx, ny, ox, oy)
        # center pressure to reduce getting stuck while chasing/escaping
        center = abs(nx - cx) + abs(ny - cy)
        # corner pressure for evader to keep reaching/holding corners
        corner = min(nx, ny, (w - 1) - nx, (h - 1) - ny)
        if is_evader:
            # maximize distance from pursuer, prefer corners when ties
            key = (d, -corner, -center, -((nx == ox and ny == oy)))
        else:
            # minimize distance to pursuer; discourage being blocked and drifting
            key = (-d, center, -corner, ((nx == ox and ny == oy)))
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]