def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        # Deterministic fallback: move toward center while roughly keeping away from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx - sign(ox - x), cy - sign(oy - y)
        dx = sign(tx - x)
        dy = sign(ty - y)
        return [dx, dy]

    # Pick target by advantage: maximize (opp_dist - self_dist), then prefer closer self, then lexicographic
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = abs(rx - x) + abs(ry - y)
        d_opp = abs(rx - ox) + abs(ry - oy)
        adv = d_opp - d_me
        key = (adv, -d_me, -d_opp, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Greedy step toward target while avoiding obstacles; tie-break deterministically
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_new = abs(tx - nx) + abs(ty - ny)
        d_old = abs(tx - x) + abs(ty - y)
        # Prefer decreasing distance to target; if equal, prefer increasing advantage; then lexicographic
        d_opp_new = abs(tx - ox - dx) + abs(ty - oy - dy)
        d_opp_old = abs(tx - ox) + abs(ty - oy)
        score = (-(d_new - d_old), (d_opp_new - d_new), -d_new, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_step = (dx, dy)

    dx, dy = best_step
    return [int(dx), int(dy)]