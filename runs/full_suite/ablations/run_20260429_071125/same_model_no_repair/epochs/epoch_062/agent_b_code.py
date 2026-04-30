def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    t = observation.get("turn_index", 0)

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]

    # If no resources, maximize distance from opponent while staying valid.
    if not res:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                val = cheb(nx, ny, ox, oy)
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]
        return best_move

    # Denial/race blend that changes with turn parity (materially different from pure race).
    # Denial prefers resources where opponent is relatively farther than us; also adds repulsion from opponent.
    denial_weight = 2.2 if (t % 2 == 0) else 1.3
    repulse_weight = 0.35 if (t % 3 == 0) else 0.2

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (inb(nx, ny) and (nx, ny) not in obstacles):
            continue

        my_d = 10**9
        opp_d = 10**9
        best_denial = -10**18

        for rx, ry in res:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            if d1 < my_d: my_d = d1
            if d2 < opp_d: opp_d = d2
            # Denial score: make this resource attractive when opponent isn't as close as we are.
            # (Higher opp_d - my_d => more denial potential)
            denom = (d2 - d1)
            if denom > best_denial: best_denial = denom

        # Combine: target closeness plus denial potential, and small repulsion from opponent.
        val = (-my_d) + denial_weight * best_denial + repulse_weight * cheb(nx, ny, ox, oy) - 0.06 * opp_d

        # Deterministic tie-break: prefer closer to board center, then lexicographic move order.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        center_pen = cheb(nx, ny, cx, cy)
        val -= 0.001 * center_pen

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move