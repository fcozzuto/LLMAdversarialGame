def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = (0, 0)
    best = None

    # Deterministic tie-break: prefer moves with smaller abs(dx)+abs(dy), then dx, then dy
    def tiebreak(dx, dy):
        return (abs(dx) + abs(dy), dx, dy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy

        d2 = dist2(nx, ny, ox, oy)
        # Pursuer: minimize distance to opponent; Evader: maximize it.
        # Also bias toward progress in the axis where separation is largest.
        sep_x = abs(nx - ox)
        sep_y = abs(ny - oy)
        cheb = max(sep_x, sep_y)

        # Small obstacle-aware term: prefer not to end adjacent to obstacles (except if already forced).
        obs_adj = 0
        for ax, ay in obs:
            if abs(nx - ax) + abs(ny - ay) == 1:
                obs_adj += 1

        if is_evader:
            score = (d2, cheb, -obs_adj)
            better = best is None or score > best
            if better or (best == score and tiebreak(dx, dy) < tiebreak(*best_move)):
                best = score
                best_move = (dx, dy)
        else:
            # Higher score is better: invert distance.
            score = (-d2, cheb, -obs_adj)
            better = best is None or score > best
            if better or (best == score and tiebreak(dx, dy) < tiebreak(*best_move)):
                best = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]