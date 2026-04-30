def choose_move(observation):
    turn_index = observation.get("turn_index", 0)
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Target the closest non-blocked resource if available
    best_res = None
    best_score = None
    for r in resources:
        r = tuple(r)
        if r in obstacles:
            continue
        d_me = dist_manhattan((sx, sy), r)
        d_opp = dist_manhattan((ox, oy), r)
        score = d_opp - d_me  # prefer resources closer to me than to opponent
        if best_score is None or score > best_score:
            best_score = score
            best_res = r

    if best_res is not None:
        tx, ty = best_res
    else:
        # No resource target: push toward center but keep distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        # choose int target near center
        tx = int(round(cx))
        ty = int(round(cy))

    # Evaluate all 9 possible moves and pick the best by simple heuristic:
    # prefer moves that move toward tx,ty, avoid obstacles and bounds, and avoid landing on opponent
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # prefer moving toward target
        d_to_target = dist_manhattan((nx, ny), (tx, ty))
        d_to_opp = dist_manhattan((nx, ny), (ox, oy))
        score = -d_to_target - (0 if d_to_opp > 1 else 5)  # discourage stepping near opponent
        if score > best_score:
            best_score = score
            best_mv = (dx, dy)

    # Ensure we always return valid delta
    dx, dy = best_mv
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        dx, dy = 0, 0
    return [dx, dy]