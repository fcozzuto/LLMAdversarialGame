def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Deterministic safe default: stay if no legal moves
    best_move = (0, 0)
    best_val = -10**18

    # If there are resources, chase the nearest one (by current manhattan)
    if resources:
        tgt = min(resources, key=lambda r: md(sx, sy, r[0], r[1]))
        tx, ty = tgt
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            val = 0
            d_self = md(nx, ny, tx, ty)
            d_opp = md(nx, ny, ox, oy)
            val += -2 * d_self
            val += 0.5 * d_opp
            val += (1 if (nx, ny) == (tx, ty) else 0)
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
    else:
        # Otherwise, maximize distance from opponent while staying legal/deterministic
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d_opp = md(nx, ny, ox, oy)
            val = d_opp
            val += (1 if (nx, ny) == (sx, sy) else 0)  # deterministic preference to stay on ties
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]