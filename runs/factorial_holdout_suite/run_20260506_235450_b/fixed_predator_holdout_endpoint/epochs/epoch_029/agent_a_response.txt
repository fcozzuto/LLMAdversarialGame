def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Select move by maximizing expected advantage over the set of resources.
    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        total = 0
        # Greedy contest: prefer states where we are closer than opponent to many resources,
        # and especially where we are closer to at least one soon.
        closest_us = 10**9
        closest_opp = 10**9
        for rx, ry in resources:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            if our_d < closest_us:
                closest_us = our_d
            if opp_d < closest_opp:
                closest_opp = opp_d
            # Advantage shaping: huge reward for being strictly ahead.
            diff = opp_d - our_d
            if diff > 0:
                total += 50 + min(25, diff * 3)
            else:
                # If behind, still prefer reducing the gap to deny.
                total += max(-60, diff * 4)
        # Extra: if we are already closer to the overall closest resource than opponent, lean in.
        total += 8 * (closest_opp - closest_us)
        # Deterministic tie-break: prefer smaller move magnitude, then lexicographic.
        move_mag = abs(dx) + abs(dy)
        key = (total, -move_mag, -dx, -dy, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move