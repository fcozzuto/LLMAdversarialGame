def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Deterministic move preference order
    pref = sorted(moves, key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    # Center bias for tie-breaking
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for dx, dy in pref:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)

        # Pursuer: minimize distance (capture radius is 0)
        # Evader: maximize distance
        if is_evader:
            primary = dist
        else:
            primary = -dist

        # Avoid stepping into opponent's immediate neighborhood when possible
        opp_adj = 0
        # Count how many opponent-neighbor positions could be captured next move (one-step)
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                tx, ty = ox + ex, oy + ey
                if tx == nx and ty == ny:
                    if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                        opp_adj = 1
        # Center tie-break
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        if best_key is None:
            best_key = (primary, -opp_adj, center_bias, dx, dy)
            best = [dx, dy]
        else:
            key = (primary, -opp_adj, center_bias, dx, dy)
            if key > best_key:
                best_key = key
                best = [dx, dy]

    return best if best is not None else [0, 0]