def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = str(observation.get("self_role", "") or "").lower()
    is_pursuer = any(k in role_self for k in ("pursuer", "chaser", "hunter"))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def obs_prox(nx, ny):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    pen += 1
        return pen

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            val = -10**9 if is_pursuer else 10**9
        else:
            d = cheb(nx, ny, ox, oy)
            prox = obs_prox(nx, ny)
            if is_pursuer:
                val = -d * 100 - prox * 2
                # Prefer moving toward capture line: reduce both coordinates' distance if possible
                val += -abs((nx - ox)) - abs((ny - oy))
            else:
                val = d * 100 - prox * 2
                # Prefer fleeing while keeping away from obstacles
                val += abs((nx - ox)) + abs((ny - oy))
        if best_val is None or (val > best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]