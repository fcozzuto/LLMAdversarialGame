def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose a resource to maximize how "contested" it is against the opponent.
    if resources:
        best = None
        for rx, ry in resources:
            # Chebyshev distance for 8-dir movement (matches allowed deltas).
            d1 = max(abs(rx - sx), abs(ry - sy))
            d2 = max(abs(rx - ox), abs(ry - oy))
            # Value: prefer resources opponent is closer to (so we can deny) while still reachable.
            # Tie-break: closer to us and then more central (to spread risk).
            dist_center = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
            val = (d2 - d1) * 10 - d1 - 0.01 * dist_center
            cand = (val, -d1, -dist_center, rx, ry)
            if best is None or cand > best:
                best = cand
        _, _, _, tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Greedy step toward target with deterministic tie-breaking, avoiding obstacles.
    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cur_d = max(abs(tx - sx), abs(ty - sy))
        nxt_d = max(abs(tx - nx), abs(ty - ny))
        # Prefer decreasing distance; if equal, prefer increasing opponent distance (deny).
        opp_d = max(abs(tx - ox), abs(ty - oy))
        opp_n_d = max(abs(tx - ox - dx), abs(ty - oy - dy))  # deterministic proxy, not exact opponent move

        step_score = (cur_d - nxt_d) * 100 + (opp_n_d - opp_d) * 1 - (abs(nx - ox) + abs(ny - oy)) * 0.01
        cand = (step_score, -nxt_d, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = [dx, dy]

    if best_move is None:
        # Fallback: move that is valid and stays safe.
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]