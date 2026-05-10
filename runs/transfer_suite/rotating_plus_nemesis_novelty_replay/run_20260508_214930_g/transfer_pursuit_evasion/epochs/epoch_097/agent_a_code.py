def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = not any(k in role for k in ("evader", "runner", "fugitive"))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obs

    # Prefer deterministic tie-breaking: lexicographic on (dx,dy) from deltas order.
    best_move = (0, 0)
    best_val = -10**18 if is_pursuer else 10**18

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            val = -10**9 if is_pursuer else -10**18
        else:
            d = manh(nx, ny, ox, oy)
            # wall-run bias for evader; chase/intercept bias for pursuer
            near_wall = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            wall_side = (nx == 0 and dx == 0) or (nx == w - 1 and dx == 0) or (ny == 0 and dy == 0) or (ny == h - 1 and dy == 0)

            if is_pursuer:
                # Move closer; also reduce opponent alignment error (prefer matching x or y) when possible.
                align = min(abs(nx - ox), abs(ny - oy))
                val = -d * 10 - align * 2 + (5 if near_wall else 0) + (2 if wall_side else 0)
            else:
                # Move away; keep to walls to exploit wall-running; avoid giving pursuer easy straight capture routes by minimizing step-alignment.
                align = min(abs(nx - ox), abs(ny - oy))
                val = d * 10 + (3 if near_wall else 0) + (1 if wall_side else 0) - align * 0.8

        if is_pursuer:
            if val > best_val + 1e-12:
                best_val, best_move = val, (dx, dy)
        else:
            if val < best_val - 1e-12:
                best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]