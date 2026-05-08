def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evad" in self_role) or ("evader" in self_role) or ("escape" in self_role) or ("runner" in self_role)
    if ("purs" in self_role) and is_evader:
        is_evader = False
    if ("purs" in opp_role) and ("evad" in self_role or "evader" in self_role):
        is_evader = True

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b):
        # Chebyshev works well for diagonal movement
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if is_evader:
        # Run to the farthest corner deterministically while avoiding obstacles.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        # Target corner farthest from pursuer (opponent position).
        target = max(corners, key=lambda c: dist(c, (ox, oy)))
        # If target cell is blocked, pick next best corner.
        if target in obstacles:
            corners_sorted = sorted(corners, key=lambda c: -dist(c, (ox, oy)))
            for c in corners_sorted:
                if c not in obstacles:
                    target = c
                    break

        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if dx == 0 and dy == 0:
                    pass
                if valid(nx, ny):
                    # Prefer increasing distance from opponent; break ties by heading to target.
                    moves.append((dist((nx, ny), (ox, oy)), -dist((nx, ny), target), dx, dy))
        # Deterministic tie-break via tuple ordering: first term larger, second smaller -> use as stored.
        if moves:
            moves.sort(reverse=True)
            _, _, dx, dy = moves[0]
            return [int(dx), int(dy)]
        return [0, 0]

    # Pursuer: minimize distance to evader with obstacle-aware greedy step.
    # Deterministic move ordering: dx then dy.
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist((nx, ny), (ox, oy))
            # Tie-break: prefer moves with larger dx/dy towards opponent (still deterministic).
            bias = -abs((nx - ox)) - abs((ny - oy))
            cand = (d, bias, dx, dy)
            if best is None or cand < best:
                best = cand
    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]