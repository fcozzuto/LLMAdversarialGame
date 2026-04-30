def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Move toward opponent if empty resources (still deterministic)
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        return [dx, dy]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Score based on advantage over opponent on the single best target resource
        # (higher is better).
        max_adv = -10**18
        min_self = 10**18
        min_opp = 10**18
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            if d_me < min_self:
                min_self = d_me
            if d_opp < min_opp:
                min_opp = d_opp
            adv = d_opp - d_me  # positive means we are closer than opponent
            if adv > max_adv:
                max_adv = adv

        # If we can be closer than opponent on some resource, strongly prefer that.
        # Otherwise, prioritize reducing our distance while also not making opponent closer.
        if max_adv >= 0:
            score = 10_000 * max_adv - 5 * min_self + 2 * min_opp
        else:
            score = -3 * min_self + 1 * min_opp  # both negative/positive handled deterministically

        # Small tie-breaker: avoid stepping adjacent to opponent (reduces contested churn)
        if max(abs(ox - nx), abs(oy - ny)) <= 1 and (nx, ny) != (ox, oy):
            score -= 3

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]