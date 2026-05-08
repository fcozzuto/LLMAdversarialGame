def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursur" in role)

    obst = set()
    for p in observation.get("obstacles", []):
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Greedy with obstacle-aware penalty; pursuer minimizes, evader maximizes.
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)

        # Penalty if move is adjacent to obstacles (evader/ pursuer both avoid getting boxed).
        adj = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (nx + ax, ny + ay) in obst:
                adj += 1

        # Encourage moves that head into capture (pursuer) or away (evader).
        # If we can step onto opponent, choose immediately when pursuer.
        if pursuer and nx == ox and ny == oy:
            return [dx, dy]

        # Slightly prefer staying away from center lines if evading wall-runner: keep lateral motion.
        lateral = abs(dy)
        bias = (0.03 * lateral if not pursuer else -0.01 * lateral)

        # Main objective plus obstacle penalty.
        val = (d + 0.45 * adj - bias) if not pursuer else (d + 0.35 * adj + bias)

        # Tie-break deterministically by fixed delta order.
        if best_val is None or (val < best_val if pursuer else val > best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]