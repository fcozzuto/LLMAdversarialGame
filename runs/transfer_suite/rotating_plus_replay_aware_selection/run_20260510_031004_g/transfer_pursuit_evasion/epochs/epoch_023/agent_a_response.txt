def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role
    obs_list = observation.get("obstacles", []) or []
    obs_set = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set

    def dist2(nx, ny):
        dx, dy = nx - ox, ny - oy
        return dx * dx + dy * dy

    def obstacle_pressure(nx, ny):
        # Penalize being close to obstacles (evader) or being trapped near obstacles (pursuer)
        pr = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obs_set:
                    pr += 2
                if (nx + ax, ny + ay) in obs_set and abs(ax) + abs(ay) == 1:
                    pr += 2
        return pr

    # Deterministic tie-break order: by (best_score, -dist/obstacle_pressure, dx, dy)
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = dist2(nx, ny)
        opress = obstacle_pressure(nx, ny)

        # Capture on same cell (pursuer). Evader tries to avoid it.
        if nx == ox and ny == oy:
            score = 1e9 if not evader else -1e9
        else:
            if evader:
                # Maximize separation; avoid obstacles; discourage moves that reduce room.
                score = d - 0.7 * opress
            else:
                # Minimize separation; avoid blocking self near obstacles.
                score = -d - 0.7 * opress

        if best_score is None:
            best_score = score
            best_move = (dx, dy)
        else:
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
            elif score == best_score:
                # Prefer moves with larger x then y for determinism (different from previous static patterns)
                if (dx, dy) > best_move:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]