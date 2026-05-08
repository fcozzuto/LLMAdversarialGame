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

    def obst_cost(x, y):
        if (x, y) in obstacles: return 10**7
        if not obstacles: return 0
        c = 0
        for ax, ay in obstacles:
            d = abs(ax - x) + abs(ay - y)
            if d == 0: return 10**7
            if d == 1: c += 120
            elif d == 2: c += 28
            elif d == 3: c += 12
            elif d <= 5: c += 5
        return c

    def edge_bias(x, y):
        # mild bias away from hugging edges; helps vs wall-running evaders
        return (min(x, w - 1 - x) + min(y, h - 1 - y))

    best_dxdy = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        d = cheb(nx, ny)
        c = obst_cost(nx, ny)
        if evading:
            # maximize distance; prefer more central squares; slight penalty near obstacles
            val = (d * 1000) + (edge_bias(nx, ny) * 2) - c
        else:
            # minimize distance; avoid obstacles; also steer to reduce opponent's "escape corridor"
            val = (-d * 1000) + (edge_bias(nx, ny) * 1) - c
        if best_val is None or val > best_val:
            best_val = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]