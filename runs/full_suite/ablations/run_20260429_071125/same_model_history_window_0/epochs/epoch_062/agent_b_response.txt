def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Pick a resource: prefer ones we're closer to than opponent, then tie-break by farther from opponent
    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        dS = dist2((sx, sy), (rx, ry))
        dO = dist2((ox, oy), (rx, ry))
        key = (0 if dS <= dO else 1, dS, -dO, rx + ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No known resources: drift away from opponent toward center
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Discourage moving into opponent's cell
        on_op = (nx == ox and ny == oy)
        dT = dist2((nx, ny), (tx, ty))
        dO = dist2((nx, ny), (ox, oy))
        # Primary: closer to target; Secondary: keep distance from opponent; Tertiary: avoid opponent cell
        score = (dT, -dO, 1 if on_op else 0, dx == 0 and dy == 0, nx * 100 + ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]