def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        # retreat/pressure: move to maximize distance from opponent (avoid being intercepted)
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in moves:
            v = man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Heuristic: choose the move that maximizes (opponent_reach - self_reach) for some target,
    # with a bias to reduce both distances; if ahead, keep closing on that target.
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        best_for_move = -10**18
        for rx, ry in resources:
            sd0 = man(sx, sy, rx, ry)
            od0 = man(ox, oy, rx, ry)
            sd1 = man(nx, ny, rx, ry)
            od1 = man(ox, oy, rx, ry)

            before_gap = od0 - sd0  # positive => opponent closer (we're behind)
            after_gap = od1 - sd1   # positive => still behind after move
            gap_improve = before_gap - after_gap  # positive => we improved our relative race

            # Prefer moves that make us ahead (after_gap <= 0), else improve toward ahead.
            lead_bonus = 30 if after_gap <= 0 else 0
            closeness_bias = -0.5 * (sd1 + 0.2 * od1)
            # Also ensure the target is not extremely bad to chase
            target_reach = -0.1 * sd1

            v = 6.0 * gap_improve + lead_bonus + closeness_bias + target_reach
            if v > best_for_move:
                best_for_move = v
        if best_for_move > best_score:
            best_score = best_for_move
            best = (dx, dy)

    return [best[0], best[1]]