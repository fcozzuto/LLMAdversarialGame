def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles", []):
        obstacles.add((p[0], p[1]))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_move = [0, 0]
    # Deterministic bias: prefer moves with smallest dx, then dy in lexicographic order.
    move_order = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    move_order = [m for m in move_order if m in dirs]

    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Find the resource that gives us the best "dominance" from the next position.
        # Dominance = our_dist - opp_dist (more negative is better).
        best_key_for_move = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            slack = sd - od
            # Key: (most negative slack, then shorter our dist, then top-left preference)
            key = (slack, sd, rx + ry, rx, ry)
            if best_key_for_move is None or key < best_key_for_move:
                best_key_for_move = key

        if best_key_for_move is None:
            continue
        # Add slight anti-lock: prefer not moving directly toward opponent if equal dominance.
        opp_step = (abs(nx - ox) + abs(ny - oy))
        key_overall = (best_key_for_move[0], best_key_for_move[1], best_key_for_move[2], best_key_for_move[3], best_key_for_move[4], opp_step)
        if best is None or key_overall < best:
            best = key_overall
            best_move = [dx, dy]

    return best_move