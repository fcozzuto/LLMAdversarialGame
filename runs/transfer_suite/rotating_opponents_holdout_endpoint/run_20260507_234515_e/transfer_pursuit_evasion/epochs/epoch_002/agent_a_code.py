def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    self_role = (observation.get("self_role") or "").lower()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                c += 1
        return c

    is_pursuer = "pursuer" in self_role
    best_mv = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d2 = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)

        if is_pursuer:
            # Minimize distance; tiebreak: more free space
            score = -d2 * 1000 + free_neighbors(nx, ny)
            better = best_score is None or score > best_score or (score == best_score and (dx, dy) < best_mv)
        else:
            # Maximize distance; prefer safer squares; also drift to farthest corner from opponent
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_bias = (abs(far_corner[0] - nx) + abs(far_corner[1] - ny))
            score = d2 * 1000 + free_neighbors(nx, ny) * 10 + corner_bias
            better = best_score is None or score > best_score or (score == best_score and (dx, dy) < best_mv)

        if better:
            best_score = score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]