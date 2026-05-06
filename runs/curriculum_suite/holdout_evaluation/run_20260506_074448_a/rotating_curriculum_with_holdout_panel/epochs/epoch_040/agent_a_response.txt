def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # Deterministic "safety sweep": prefer moving toward middle band to avoid being cornered by row sweeps.
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        # Try diagonal first to change parity
        for ddx, ddy in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    # Pick a resource where we are relatively closer than opponent.
    # Value: (opponent advantage) - (distance pressure) with light center bias to reduce dithering.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        my_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        rel = opp_d - my_d  # positive means I'm closer
        center = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)) * 0.01
        # Prefer resources with big rel; break ties by closer my_d and center.
        score = rel * 10.0 + center - my_d * 0.3
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    rx, ry = best_r

    # Move one step greedily toward chosen resource, but avoid moves that give opponent a closer approach.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_d_next = man(nx, ny, rx, ry)
        opp_d_next_to_target = man(ox, oy, rx, ry)
        # Small opponent pressure: prefer states where my lead over opponent at/near target is stronger.
        # Since opponent position doesn't change, include a "helpful blocking" term via distance to opponent.
        lead = opp_d_next_to_target - my_d_next
        opp_dist = man(nx, ny, ox, oy)
        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        edge_bias = edge * 0.02
        # Prefer reducing my distance to target primarily; then increase lead; then increase separation from opponent.
        val = -my_d_next * 2.0 + lead * 3.0 + opp_dist * 0.05 + edge_bias
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]