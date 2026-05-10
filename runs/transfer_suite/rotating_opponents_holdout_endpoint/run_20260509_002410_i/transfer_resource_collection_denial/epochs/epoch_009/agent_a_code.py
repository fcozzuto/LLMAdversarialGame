def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def in_bounds(x, y): return 0 <= x < w and 0 <= y < h

    obstacle_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacle_set.add((p[0], p[1]))

    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Target: maximize our advantage = (opp_dist - self_dist), prefer we arrive sooner.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacle_set:
            continue
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd, -abs(rx - ox) - abs(ry - oy), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    # Greedy step toward target with local obstacle avoidance.
    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (None, None, None)  # (key, nx, ny)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
            continue
        d_now = manh(nx, ny, tx, ty)
        d_opp = manh(nx, ny, ox, oy)
        # Prefer reducing distance to target; then increase distance from opponent; then prefer deterministic ordering.
        key = (-d_now, d_opp, -dx, -dy)
        if best_move[0] is None or key > best_move[0]:
            best_move = (key, nx, ny)

    if best_move[0] is None:
        return [0, 0]
    nx, ny = best_move[1], best_move[2]
    dx, dy = nx - sx, ny - sy
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]