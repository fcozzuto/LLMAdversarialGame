def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Drift to center while respecting obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = -cheb(nx, ny, cx, cy)
                if val > best[1]:
                    best = ((dx, dy), val)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    # Evaluate each move by the best resource "advantage" we can create next.
    best_move = (0, 0)
    best_val = -10**18

    # Small deterministic tie-breaker: prioritize cardinal-ish moves over diagonals, then lexicographic.
    def move_tb(dx, dy):
        # Lower is better
        diag = 1 if dx != 0 and dy != 0 else 0
        return (diag, abs(dx) + abs(dy), dx, dy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        best_r_val = -10**18
        # Primary: maximize advantage (opponent distance - our distance).
        # Secondary: minimize our distance; also slight preference for resources closer to board center.
        center_x, center_y = (w - 1) // 2, (h - 1) // 2
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            gain = op_d - my_d
            # Reward immediate/near capture; encourage blocking by making gain large.
            val = gain * 1000 - my_d * 3 - cheb(rx, ry, center_x, center_y) * 0.05
            if val > best_r_val:
                best_r_val = val

        # If we can't reach any useful resource, still minimize distance to the closest one.
        if best_r_val == -10**18:
            closest = min((cheb(nx, ny, rx, ry) for rx, ry in resources), default=0)
            best_r_val = -closest

        if best_r_val > best_val:
            best_val = best_r_val
            best_move = (dx, dy)
        elif best_r_val == best_val:
            # Deterministic tie-break
            if move_tb(dx, dy) < move_tb(best_move[0], best_move[1]):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]