def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    evading = any(k in role for k in ("evade", "runner", "flee", "evasion", "evader"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x, y): 
        dx, dy = abs(ox - x), abs(oy - y)
        return dx if dx > dy else dy

    def obst_pen(x, y):
        if (x, y) in obstacles: return 10**7
        p = 0
        for ax, ay in obstacles:
            d = abs(ax - x) + abs(ay - y)
            if d == 0: return 10**7
            if d == 1: p += 60
            elif d == 2: p += 18
            elif d == 3: p += 8
            elif d <= 5: p += 3
        return p

    def edge_pen(x, y):
        # discourage being too often glued to edges if we're not making progress
        return (min(x, w-1-x) + min(y, h-1-y)) * 0

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            val = -10**18 if evading else 10**18
        else:
            d = cheb(nx, ny)
            p = obst_pen(nx, ny)
            progress = -d if evading is False else d
            # If evading: prefer corner farthest from pursuer; also avoid obstacles.
            if evading:
                corner_dist = min(abs(nx-(0 if ox < w//2 else w-1)) + abs(ny-(0 if oy < h//2 else h-1)),
                                   abs(nx-(w-1 if ox < w//2 else 0)) + abs(ny-(h-1 if oy < h//2 else 0)))
                val = (d * 10) - p + (corner_dist * 0.1) + edge_pen(nx, ny)
            else:
                # If pursuing: minimize distance; if close, prioritize blocking with obstacle avoidance.
                val = (-d * 10) - p + edge_pen(nx, ny) + (0.01 if (d == 0) else 0)
        if best is None or ((evading and val > best_val) or (not evading and val < best_val)):
            best, best_val = [dx, dy], val

    return [int(best[0]), int(best[1])]