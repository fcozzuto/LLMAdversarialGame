def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    role = observation.get("self_role", "pursuer")

    obstacles = set()
    for p in observation.get("obstacles", []):
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((dx, dy))

    if not cand:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # If we can capture immediately, do it.
    if role == "pursuer":
        for dx, dy in cand:
            if (sx + dx) == ox and (sy + dy) == oy:
                return [dx, dy]
    else:
        # If opponent is on our cell and we're evader (rare), maximize escaping.
        pass

    # Score: pursuer minimizes distance; evader maximizes distance.
    # Tie-breaker: prefer moves that keep us away from obstacles walls by penalizing "near-wall" less
    # and deterministic ordering by a fixed secondary heuristic.
    best = None
    best_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny, ox, oy)

        if role == "pursuer":
            val = -d
        else:
            val = d

        # Small deterministic bias to reduce oscillation and encourage staying mobile:
        # prefer diagonal movement when it doesn't block capture-chase objective.
        mobility = 0
        if dx != 0 and dy != 0:
            mobility = 1
        if dx == 0 and dy == 0:
            mobility = -1

        # Penalize being adjacent to obstacles (would constrain future).
        adj_pen = 0
        for ax, ay in obstacles:
            if dist2(nx, ny, ax, ay) == 1:
                adj_pen += 1

        val = val + 0.1 * mobility - 0.05 * adj_pen

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    return [int(best[0]), int(best[1])]