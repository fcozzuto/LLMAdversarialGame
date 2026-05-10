def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = observation.get("self_role", "pursuer")

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in blocked

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return max(abs(ax - bx), abs(ay - by))

    def corner_bias(x, y):
        return min(x, w - 1 - x) + min(y, h - 1 - y)

    my_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            my_moves.append((dx, dy, nx, ny))
    if not my_moves:
        return [0, 0]

    opp_role = "evader" if role == "pursuer" else "pursuer"

    best = None
    best_val = None
    d_cur = dist((sx, sy), (ox, oy))

    for dx, dy, nx, ny in my_moves:
        # Opponent responds with a deterministic 1-step heuristic.
        best_opp = None
        best_opp_val = None
        for odx, ody in moves:
            ex, ey = ox + odx, oy + ody
            if not valid(ex, ey):
                continue
            d_after = dist((nx, ny), (ex, ey))
            if opp_role == "evader":
                val = (d_after, -corner_bias(ex, ey))  # maximize distance, prefer edge
            else:
                val = (-d_after, corner_bias(ex, ey))   # minimize distance, prefer center a bit
            if best_opp_val is None or val > best_opp_val:
                best_opp_val = val
                best_opp = (ex, ey)

        if best_opp is None:
            ex, ey = ox, oy
        else:
            ex, ey = best_opp

        d_final = dist((nx, ny), (ex, ey))
        # Capture next turn: if we can step onto opponent immediately, prioritize heavily.
        capture_bonus = 0 if (nx, ny) != (ox, oy) else 1000

        if role == "pursuer":
            val = (-d_final, capture_bonus, d_cur - d_final, corner_bias(nx, ny))
            better = best_val is None or val > best_val
        else:
            val = (d_final, capture_bonus, -(d_cur - d_final), -corner_bias(nx, ny))
            better = best_val is None or val > best_val

        if better:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]