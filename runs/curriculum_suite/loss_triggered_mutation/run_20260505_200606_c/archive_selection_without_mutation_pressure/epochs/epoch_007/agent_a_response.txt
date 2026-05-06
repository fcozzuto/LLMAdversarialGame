def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp(v, lo, hi):
        return lo if v < lo else (hi if v > hi else v)

    # Identify the resource the opponent is most likely to take (closest by king-metric).
    tx, ty = min(resources, key=lambda r: kdist(ox, oy, r[0], r[1]))

    # Choose a guard point roughly along the line opponent->target, biased toward our side.
    xmid = (ox + tx) // 2
    ymid = (oy + ty) // 2
    guard_candidates = [(xmid, ymid), (xmid, clamp(ymid + (1 if ty > oy else -1), 0, h - 1)), (clamp(xmid + (1 if tx > ox else -1), 0, w - 1), ymid)]
    guard_candidates2 = []
    for gx, gy in guard_candidates:
        if (gx, gy) not in obstacles:
            guard_candidates2.append((gx, gy))
    if not guard_candidates2:
        guard_candidates2 = [(xmid, ymid)]

    best_score = None
    best_move = [0, 0]
    # Score: prefer moves that reduce distance to a guard point, and (secondarily) increase the opponent's time to the chosen target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue

        our_to_guard = min(kdist(nx, ny, gx, gy) for gx, gy in guard_candidates2)
        op_to_target = kdist(ox, oy, tx, ty)

        # If we can get closer to the target than the opponent after this move, heavily prioritize that.
        our_to_target = kdist(nx, ny, tx, ty)
        win_pressure = 0
        if our_to_target < op_to_target:
            win_pressure = 50 - our_to_target

        # Also slightly prefer moving toward the opponent-target direction (denial pressure).
        dir_boost = 0
        if kdist(nx, ny, tx, ty) < kdist(sx, sy, tx, ty):
            dir_boost = 3

        score = (-our_to_guard) + (2 * -op_to_target) + win_pressure + dir_boost

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move