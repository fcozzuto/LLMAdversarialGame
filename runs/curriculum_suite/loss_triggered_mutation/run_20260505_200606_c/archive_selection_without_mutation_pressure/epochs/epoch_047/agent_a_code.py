def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Precompute nearest obstacle distance for soft obstacle avoidance
    # (only local, deterministic: check 8 neighbors)
    def obstacle_pen(nx, ny):
        p = 0
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            tx, ty = nx + dx, ny + dy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                p += 1
        return p

    best_move = (0, 0)
    best_val = -10**18

    # Our move evaluation: maximize a deterministic "win-the-resource" score.
    # Score favors resources where we are closer than opponent, and proximity overall.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        our_best = -10**18
        for rx, ry in resources:
            ou = cheb(nx, ny, rx, ry)
            op = cheb(ox, oy, rx, ry)
            # If we can reach first, it's strongly good; otherwise discouraged.
            reach_gap = op - ou  # positive => we are closer/equal
            # Large weight to reach gap, smaller to our distance.
            val = 5.0 * reach_gap - 0.25 * ou
            # Encourage immediate pickup
            if ou == 0:
                val += 100.0
            if ou == 1:
                val += 4.0
            # Slightly discourage moving away from board corners (helps consistency)
            val -= 0.05 * (abs(rx - nx) + abs(ry - ny))
            if val > our_best:
                our_best = val

        # Also lightly penalize getting adjacent to obstacles to avoid stuck paths
        val = our_best - 0.6 * obstacle_pen(nx, ny)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]