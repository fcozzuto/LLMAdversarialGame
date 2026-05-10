def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    is_evader = "evader" in (observation.get("self_role", "") or "").lower()
    role = "evader" if is_evader else "pursuer"

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Prefer deterministic corner-ish tie-break: push x/y toward extreme away/toward opponent.
    if is_evader:
        tx = 0 if ox >= (w - 1) / 2 else w - 1
        ty = 0 if oy >= (h - 1) / 2 else h - 1
    else:
        tx = 0 if ox < (w - 1) / 2 else w - 1
        ty = 0 if oy < (h - 1) / 2 else h - 1

    best = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dist = abs(nx - ox) + abs(ny - oy)
        near_obs = 0
        for adx, ady in ((-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            px, py = nx + adx, ny + ady
            if (px, py) in obs:
                near_obs += 1

        # Corner progress term:
        corner_prog = -(abs(nx - tx) + abs(ny - ty))  # higher is better
        # Obstacle safety term:
        safety = -near_obs

        if role == "pursuer":
            # Minimize distance; secondary: move "in front" toward opponent-favored extreme and avoid obstacles.
            score = (-dist) + 0.03 * corner_prog + 0.15 * safety
        else:
            # Maximize distance; secondary: move toward opposite extreme corner and avoid obstacles.
            score = (dist) + 0.03 * corner_prog + 0.15 * safety

        if best is None or score > best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    # If all moves invalid (shouldn't happen), stay put.
    return [int(best_move[0]), int(best_move[1])]