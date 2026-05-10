def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in (observation.get("obstacles") or []):
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) and ("evader" not in opp_role)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    turn = int(observation.get("turn_index", 0))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose farthest corner for evasion / nearest corner for pursuer as deterministic tie-break.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def corner_score(cx, cy):
        return max(abs(cx - ox), abs(cy - oy))
    if is_evader:
        target_corner = max(corners, key=lambda c: corner_score(c[0], c[1]))
    else:
        target_corner = min(corners, key=lambda c: corner_score(c[0], c[1]))
    tx, ty = target_corner

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist = max(abs(ox - nx), abs(oy - ny))  # Chebyshev distance fits diagonal moves
        corner_dist = abs(tx - nx) + abs(ty - ny)
        # Deterministic secondary: prefer reducing/increasing corner_dist based on role, plus turn parity.
        key = (dist, -corner_dist if is_evader else corner_dist, (nx + ny + turn) % 2)
        if best is None:
            best = (key, (dx, dy))
        else:
            if is_evader:
                if key > best[0]:
                    best = (key, (dx, dy))
            else:
                # minimize distance: invert dist for comparison
                key2 = (-key[0], key[1], key[2])
                best_key2 = (-best[0][0], best[0][1], best[0][2])
                if key2 < best_key2:
                    best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]