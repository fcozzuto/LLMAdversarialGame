def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in (observation.get("obstacles") or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role", "")).lower()
    is_evader = "evader" in self_role or "runner" in self_role or "escape" in self_role
    # deterministic delta priority: orthogonal + then diagonals, favor progressing to reduce ties
    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def clamp_wall_pen(x, y):
        # higher when closer to walls (encourages staying away as evader)
        d = min(x, y, w - 1 - x, h - 1 - y)
        return (3 - d) if d < 3 else 0

    best_move = deltas[0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        man = abs(ddx) + abs(ddy)

        # also discourage moves that would step adjacent into blocked/near-wall dead-ends for evader
        adj_obs = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            ax, ay = nx + adx, ny + ady
            if not inside(ax, ay) or (ax, ay) in obs:
                adj_obs += 1

        if is_evader:
            score = dist2 * 10 - man - 2 * clamp_wall_pen(nx, ny) - 0.5 * adj_obs
        else:
            # pursuer: prefer smaller distance; slight preference for moving (not staying) to avoid stalling
            score = -(dist2 * 10 + man) - (0.3 if dx == 0 and dy == 0 else 0)

        if best_score is None or (score > best_score if is_evader else score > best_score):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]