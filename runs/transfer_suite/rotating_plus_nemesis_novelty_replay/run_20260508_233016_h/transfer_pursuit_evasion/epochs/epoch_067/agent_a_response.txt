def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    self_role = str(observation.get("self_role") or "")
    self_evader = "evader" in self_role.lower()

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Encourage pursuer to approach along the "most constrained" direction: steer toward the corner
    # that is farthest from the evader (opponent) to squeeze escape paths.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_score(cx, cy):
        return dist2(cx, cy, ox, oy)  # far from opponent
    target_corner = max(corners, key=lambda c: corner_score(c[0], c[1]))

    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, target_corner[0], target_corner[1])

        # obstacle proximity penalty (deterministic): closer obstacles slightly worse
        min_obs = 10**9
        for bx, by in blocked:
            dd = dist2(nx, ny, bx, by)
            if dd < min_obs:
                min_obs = dd

        # Evaluate: pursuer minimizes opponent distance and also moves toward squeeze corner.
        # Evader maximizes opponent distance and moves away from squeeze corner.
        if self_evader:
            val = (d_opp) + (-0.001 * d_corner) - (0.01 / (1 + min_obs))
        else:
            val = (-d_opp) + (0.0005 * (-d_corner)) - (0.01 / (1 + min_obs))

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # deterministic tie-break: prefer moves with smaller dx, then smaller dy, then non-stay
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]