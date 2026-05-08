def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def pos(p, default=(0, 0)):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict) and "x" in p and "y" in p:
            return int(p["x"]), int(p["y"])
        return default

    sx, sy = pos(observation.get("self_position", [0, 0]))
    ox, oy = pos(observation.get("opponent_position", [0, 0]))
    role = observation.get("self_role", "pursuer")

    obstacles = set()
    for o in (observation.get("obstacles") or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = o[0], o[1]
        elif isinstance(o, dict) and "x" in o and "y" in o:
            x, y = o["x"], o["y"]
        else:
            continue
        try:
            x, y = int(x), int(y)
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = None

    if role == "evader":
        # maximize distance; also drift toward the farthest corner among legal moves
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d_opp = dist(nx, ny, ox, oy)
            d_corner = 0
            for cx, cy in corners:
                if free(nx, ny):
                    d_corner = max(d_corner, dist(nx, ny, cx, cy))
            # small deterministic bias: prefer diagonal when tied
            val = (d_opp, d_corner, 1 if dx != 0 and dy != 0 else 0, -abs(dx) - abs(dy))
            if best is None or val > best_val:
                best, best_val = [dx, dy], val
    else:
        # pursuer: minimize distance; prefer moves that most reduce distance
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = dist(nx, ny, ox, oy)
            # bias: prefer staying closer to the opponent's current axis (stable chase)
            axis = 0
            if nx != ox:
                axis -= abs(nx - ox)
            else:
                axis += 0
            if ny != oy:
                axis -= abs(ny - oy)
            else:
                axis += 0
            val = (-d, -axis, 1 if dx == 0 or dy == 0 else 0)  # prefer non-snake diagonals when tied
            if best is None or val > best_val:
                best, best_val = [dx, dy], val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]