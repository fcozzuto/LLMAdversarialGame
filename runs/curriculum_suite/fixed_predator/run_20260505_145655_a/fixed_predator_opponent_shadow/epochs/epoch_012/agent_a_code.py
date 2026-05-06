def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Prefer moves that secure nearby resources vs opponent, while keeping pressure (closer to opponent).
    best = (0, 0)
    best_val = None
    cur_opp_d = md(x, y, ox, oy)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        my_d_opp = md(nx, ny, ox, oy)
        # tie-breaker to keep determinism among equal moves
        val = -my_d_opp * 0.05

        # Evaluate all resources, but prioritize close ones
        # (deterministic: resource order in list)
        for i, (rx, ry) in enumerate(resources):
            d_me = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            if d_me == 0:
                val += 100.0 + (20 - i)
                continue
            # If we can arrive sooner or tie, strong positive; else mild negative.
            if d_me < d_op:
                val += 30.0 / (1 + d_me) + 6.0
            elif d_me == d_op:
                val += 10.0 / (1 + d_me) + 2.0
            else:
                val -= 8.0 / (1 + d_me)
            # Small preference to reduce distance to resources overall
            val += -0.3 * d_me

        # Additional pressure: avoid getting much farther from opponent than current
        val += -max(0, my_d_opp - cur_opp_d) * 0.2

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]