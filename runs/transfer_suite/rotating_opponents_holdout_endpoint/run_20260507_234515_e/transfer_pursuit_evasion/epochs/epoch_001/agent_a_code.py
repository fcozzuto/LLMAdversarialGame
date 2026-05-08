def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_role = observation.get("self_role", "")
    opponent_role = observation.get("opponent_role", "")

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def sign(v):
        return (v > 0) - (v < 0)

    moves = [
        (0, 0), (-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 1),
        (1, -1), (1, 0), (1, 1)
    ]

    if "pursuer" in self_role.lower():
        # chase
        best = None
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            if best is None or d < best_d or (d == best_d and (dx, dy) < best):
                best = (dx, dy)
                best_d = d
        if best is not None:
            return [best[0], best[1]]
    else:
        # evade
        best = None
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            if best is None or d > best_d or (d == best_d and (dx, dy) < best):
                best = (dx, dy)
                best_d = d
        if best is not None:
            return [best[0], best[1]]

    # fallback: move directly, still deterministic
    dx = sign(ox - sx)
    dy = sign(oy - sy)
    nx, ny = sx + dx, sy + dy
    if in_bounds(nx, ny) and (nx, ny) not in obstacles:
        return [dx, dy]
    return [0, 0]