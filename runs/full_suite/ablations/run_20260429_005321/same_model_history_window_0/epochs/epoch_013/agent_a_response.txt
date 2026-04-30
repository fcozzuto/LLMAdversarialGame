def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    res_set = set((x, y) for x, y in resources)
    obs_set = set((x, y) for x, y in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        op_d = dist_cheb(nx, ny, ox, oy)
        on_res = 1 if (nx, ny) in res_set else 0

        # Evaluate best resource to pursue from this position.
        target_score = -10**12
        if resources:
            for rx, ry in resources:
                d1 = dist_cheb(nx, ny, rx, ry)
                d2 = dist_cheb(ox, oy, rx, ry)
                # Prefer resources closer to us than opponent.
                s = (-d1) + 0.5 * (d2 - d1)  # higher is better
                if s > target_score:
                    target_score = s
        else:
            target_score = 0

        # Keep a soft preference to avoid getting adjacent to opponent.
        move_score = 0
        move_score += 1200 * on_res
        move_score += 50 * target_score
        move_score += -3.0 * op_d
        if dx == 0 and dy == 0:
            move_score -= 0.5  # slight dislike to avoid stalling

        if move_score > best_score:
            best_score = move_score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best