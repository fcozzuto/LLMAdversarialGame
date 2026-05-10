def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role", "pursuer") or "pursuer").lower()
    pursuer = role != "evader"

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return (x, y) not in obstacles

    best_move = (0, 0)
    best_val = None

    # Tie-breaker order: center-ish to corners to be deterministic.
    order = sorted(moves, key=lambda m: (abs(m[0]) + abs(m[1]), m[0], m[1]))

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not free(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)

        # Greedy pursuit/evasion with a small directional bias for zigzag.
        if pursuer:
            # Prefer decreasing distance; if equal, prefer stepping toward opponent along the larger axis.
            axis = abs(nx - ox) - abs(ny - oy)  # positive => closer in y
            dir_bias = (-1 if axis > 0 else 1) * (abs(nx - ox) - abs(ny - oy))
            val = (-d, dir_bias, nx, ny)
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)
        else:
            # Prefer increasing distance; if equal, prefer moving away in the dominant axis.
            axis = abs(nx - ox) - abs(ny - oy)
            dominant = "x" if axis >= 0 else "y"
            away = (nx - ox) if dominant == "x" else (ny - oy)
            dir_bias = (1 if away > 0 else -1) * abs(away)
            val = (d, dir_bias, -nx, -ny)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]