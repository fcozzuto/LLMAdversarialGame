def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = observation.get("self_role", "pursuer")
    is_pursuer = (role == "pursuer")
    t = int(observation.get("turn_index", 0) or 0)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def edge_pen(nx, ny):
        return min(nx, w - 1 - nx) + min(ny, h - 1 - ny)

    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        nd = d2(nx, ny, ox, oy)
        if is_pursuer:
            # Cut off: minimize distance; also push toward edges of evader by minimizing edge_pen at evader side
            # and favor moves that bring us closer to the line between positions (deterministic).
            corner_bias = edge_pen(ox, oy)  # lower means evader nearer edge already; still helps to chase into corners
            line_bias = -abs((nx - ox) - (ny - oy))  # crude "diagonal line" heuristic
            val = (-nd, corner_bias, -line_bias, nx, ny)
        else:
            # Evader: maximize distance; add deterministic zigzag to foil zigzag-chasers
            zig = (1 if (t % 2 == 0) else -1)
            zig_bias = -abs((nx - sx) - zig) - abs((ny - sy) + zig)
            wall_safety = edge_pen(nx, ny)  # prefer staying away from obstacles/walls
            val = (nd, wall_safety, zig_bias, -nx if (t % 2 == 0) else nx, -ny if (t % 2 == 1) else ny)

        if best is None:
            best, best_val = (dx, dy), val
        else:
            if val > best_val:
                best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]