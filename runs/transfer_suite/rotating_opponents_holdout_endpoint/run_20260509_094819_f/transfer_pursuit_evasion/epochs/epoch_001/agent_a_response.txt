def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    self_role = observation.get("self_role", "")
    opp_role = observation.get("opponent_role", "")
    x, y = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        if (nx, ny) in obs:
            return False
        return True

    is_pursuer = ("purs" in self_role.lower()) or ("purs" in opp_role.lower() and "evad" not in self_role.lower())
    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if is_pursuer:
            # Prefer capture by reaching exact opponent position (capture_radius=0)
            score = -1000000 if (nx == ox and ny == oy) else -d2
        else:
            # Prefer survival: maximize distance and avoid moving onto pursuer
            score = -1000000 if (nx == ox and ny == oy) else d2

        key = (score, -dx, -dy) if best is None else None
        if best is None:
            best = (dx, dy)
            best_score = score
        else:
            better = score > best_score
            same = score == best_score
            if better or (same and (dx, dy) < best):
                best = (dx, dy)
                best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]