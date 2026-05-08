def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("catch" in role) or ("purs" in opp_role and "evad" not in role)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_cell(x, y):
        d = max(abs(x - ox), abs(y - oy))  # capture radius 0 -> Chebyshev
        adj_block = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not ok(nx, ny):
                    adj_block += 1
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = max(abs(x - cx) + abs(y - cy) for cx, cy in corners)
        # pursuer: minimize distance; evader: maximize distance + prefer corners while avoiding tight spots
        if is_pursuer:
            return (-d * 100 - adj_block * 2 - far_corner * 0.1, 0)
        return (d * 100 + far_corner * 2 - adj_block * 2, 0)

    best = None
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val, _ = score_cell(nx, ny)
            if best is None or (is_pursuer and val < best_val) or ((not is_pursuer) and val > best_val) or (val == best_val and (dx, dy) < best):
                best = (dx, dy)
                best_val = val
    if best is None:
        return [0, 0]
    return [best[0], best[1]]