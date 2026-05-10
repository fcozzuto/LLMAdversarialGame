def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set(obstacles)

    self_role = (observation.get("self_role") or "").lower()
    opponent_role = (observation.get("opponent_role") or "").lower()

    pursuer = ("pursur" in self_role) or ("pursuer" in self_role) or ("pursuit" in self_role)
    if "evad" in self_role:
        pursuer = False
    if "evad" in opponent_role and not ("pursur" in self_role or "pursuer" in self_role):
        pursuer = False

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist2(nx, ny):
        dx, dy = nx - ox, ny - oy
        return dx * dx + dy * dy

    def blocked(nx, ny):
        return (nx, ny) in obs

    best = None
    best_dxdy = [0, 0]
    eps = 1e-9

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d = dist2(nx, ny)
        score = d if pursuer else -d
        # Prefer staying closer to center when tied
        center_bias = -(abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * eps
        score += center_bias
        if best is None or score < best:
            best = score
            best_dxdy = [dx, dy]

    return best_dxdy if best is not None else [0, 0]