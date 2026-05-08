def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Determine whether we should pursue (reduce distance) or evade (increase distance)
    pursuer = ("pursuer" in self_role) or ("evader" not in self_role and "evader" in opp_role)
    if ("evader" in self_role) and ("pursuer" in opp_role):
        pursuer = False

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = None

    # Simple deterministic scoring:
    # - primary: Chebyshev distance to opponent (works well with diagonal moves)
    # - secondary: keep away from obstacles (avoid moves with many blocked neighbor cells)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = max(abs(nx - ox), abs(ny - oy))
        neigh_block = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            tx, ty = nx + ax, ny + ay
            if not ok(tx, ty):
                neigh_block += 1
        # Tie-breaker favors advancing (pursuer) / distancing (evader) in x then y, deterministically
        tie = (-(abs(nx - sx)), -(abs(ny - sy)))  # prefer smaller move magnitude when tied
        score = dist
        if pursuer:
            score = dist * -1
            score = score - 0.03 * neigh_block
        else:
            score = dist * 1
            score = score - 0.03 * neigh_block

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]