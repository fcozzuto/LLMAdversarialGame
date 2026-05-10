def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if p is None:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    if self_role:
        pursuer = ("evad" not in self_role)
    else:
        pursuer = ("evad" not in opponent_role) if opponent_role else True

    # Target if pursuing: opponent position. If evading: go to farthest corner from opponent.
    if pursuer:
        tx, ty = ox, oy
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort()  # deterministic tie-break
    best_move = [0, 0]
    best_score = None

    # Evaluate: pursue -> minimize distance to target, penalize proximity to obstacles; evade -> maximize distance from opponent
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        if pursuer:
            main = -(abs(nx - tx) + abs(ny - ty))
        else:
            main = abs(nx - ox) + abs(ny - oy)

        # Obstacle penalty: avoid stepping adjacent to obstacles
        adj_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs_set:
                    adj_pen += 1

        # Mild preference to keep moving generally toward/away from target corner
        drift = 0
        if not pursuer:
            drift = -((abs(nx - tx) + abs(ny - ty)) * 0.01)

        score = main - adj_pen * (1.0 if pursuer else 0.8) + drift

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]