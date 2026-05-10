def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = observation.get("self_role", "pursuer")
    env = observation.get("environment_name", "")
    if env != "pursuit_evasion":
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    if role == "pursuer":
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            d = dist(nx, ny, ox, oy)
            score = d
            # Prefer moves that keep direction towards opponent
            dir_bonus = -0.01 * (0 if dx == 0 else 1) - 0.01 * (0 if dy == 0 else 1)
            score = score + dir_bonus
            if best_val is None or score < best_val:
                best_val = score
                best_move = (dx, dy)
    else:
        # evader: maximize distance while staying safe
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs:
                continue
            d = dist(nx, ny, ox, oy)
            # Prefer fleeing in the dominant axis when possible
            flee_bonus = 0.01 * (0 if (dx == 0) else 1) + 0.01 * (0 if (dy == 0) else 1)
            score = -d + flee_bonus
            if best_val is None or score < best_val:
                best_val = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]