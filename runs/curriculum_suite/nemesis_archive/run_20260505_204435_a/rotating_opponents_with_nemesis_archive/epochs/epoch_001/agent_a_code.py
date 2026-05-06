def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((x, y) for x, y in obstacles)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(a, b, c, d):
        dx = a - c; dy = b - d
        return dx * dx + dy * dy

    # Pick target resource: prefer being relatively closer than opponent.
    if resources:
        best = None
        for rx, ry in resources:
            sd = dist2(sx, sy, rx, ry)
            od = dist2(ox, oy, rx, ry)
            score = (sd - od, sd, abs(rx - 0.5 * (w - 1)) + abs(ry - 0.5 * (h - 1)))
            if best is None or score < best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) / 2, (h - 1) / 2

    # Candidate moves: among valid steps, minimize distance to target.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (10**18, 0, 0)
    for dx, dy in moves:
        nx = clamp(sx + dx, 0, w - 1); ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obs_set:
            continue
        # If landing on a resource, strongly prefer.
        resource_bonus = -1000000 if resources and (nx, ny) in set(map(tuple, resources)) else 0
        dcur = dist2(nx, ny, tx, ty)
        # Also gently avoid moving away when possible.
        dprev = dist2(sx, sy, tx, ty)
        step_gain = dprev - dcur
        # Final objective tuple
        key = (dcur + (-1e-3) * step_gain + resource_bonus)
        if key < best_move[0]:
            best_move = (key, dx, dy)

    dx, dy = best_move[1], best_move[2]
    if int(dx) not in (-1, 0, 1) or int(dy) not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]