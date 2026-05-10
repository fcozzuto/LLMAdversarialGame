def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    turn = int(observation.get("turn_index", 0) or 0)

    def score_cell(nx, ny):
        d = abs(nx - ox) + abs(ny - oy)
        # obstacle penalty/bonus shaping
        od = 10
        if obstacles:
            od = min(abs(nx - ax) + abs(ny - ay) for (ax, ay) in obstacles)
        obstacle_term = 0
        if od <= 1:
            obstacle_term = -1000
        elif od == 2:
            obstacle_term = -50
        elif od == 3:
            obstacle_term = -10
        # bias to steer away from nearest obstacle direction slightly
        bias = (nx * 3 + ny * 5 + turn * 7) % 9  # deterministic tie-breaker
        if evader:
            # maximize distance, avoid obstacles, also prefer "toward farthest corner"
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            farcorner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_bonus = (abs(farcorn[0] - nx) + abs(farcorn[1] - ny))
            return d * 10 + corner_bonus + od + obstacle_term + bias * 1e-3
        else:
            # pursuer: minimize distance, avoid obstacles, bias toward center-ish
            center_bonus = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)
            return -d * 10 + center_bonus + od + obstacle_term + bias * 1e-3

    best_move = [0, 0]
    best_val = None
    # deterministic move ordering tweak based on parity
    start_idx = 3 if (turn & 1) else 0
    ordered = moves[start_idx:] + moves[:start_idx]

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = score_cell(nx, ny)
        if best_val is None or (v > best_val if evader else v > best_val):
            best_val = v
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]