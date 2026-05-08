def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obs}
    resources = observation.get("resources") or []

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def score_cell(x, y):
        if resources:
            bestd = 10**9
            bestr = 0
            for r in resources:
                rx, ry = r[0], r[1]
                d = abs(x - rx) + abs(y - ry)
                if d < bestd:
                    bestd = d
                    bestr = r[2] if len(r) > 2 else 1
            # Prefer being closer; break ties by preferring cells closer to opponent (denying)
            return bestd - 0.1 * bestr - 0.01 * (abs(x - ox) + abs(y - oy))
        # No resources: chase/intercept by minimizing distance to opponent
        return abs(x - ox) + abs(y - oy)

    best = None
    best_pos = (sx, sy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        s = score_cell(nx, ny)
        if best is None or s < best:
            best = s
            best_pos = (nx, ny)

    dx, dy = best_pos[0] - sx, best_pos[1] - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]