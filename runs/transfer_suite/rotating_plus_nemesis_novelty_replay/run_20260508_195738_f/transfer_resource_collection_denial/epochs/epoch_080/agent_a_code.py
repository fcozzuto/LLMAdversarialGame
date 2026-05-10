def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_for(pos):
        if not resources:
            return 0, None
        best_d = None
        best_r = None
        for r in resources:
            d = md(pos, r)
            if best_d is None or d < best_d:
                best_d, best_r = d, r
        return best_d, best_r

    best_my_d, best_my_r = best_for((sx, sy))
    best_my_d = best_my_d if best_my_d is not None else 10**9

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_me, r = best_for((nx, ny))
        d_op, _ = best_for((ox, oy))  # reference current best for opponent; cheap and deterministic
        if not resources:
            val = -(abs(dx) + abs(dy))
        else:
            # Prefer smaller distance for us to our nearest resource, and penalize if opponent is closer to that same resource.
            d_op_to_same = md((ox, oy), r) if r is not None else 10**9
            val = (best_my_d - d_me) * 1000 + (d_op_to_same - d_me) * 30 - (abs(dx) + abs(dy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]