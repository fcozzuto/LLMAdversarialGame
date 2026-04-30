def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def mindist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if resources:
        best = None
        best_val = -10**9
        for r in resources:
            d1 = mindist((x, y), r)
            d2 = mindist((ox, oy), r)
            adv = d2 - d1
            val = adv * 100 - d1  # prioritize advantage, then closeness
            if val > best_val:
                best_val = val
                best = r
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = -10**12
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        d_me = mindist((nx, ny), (tx, ty))
        d_op = mindist((ox, oy), (tx, ty))
        # Prefer reducing my distance; also keep/extend advantage over opponent
        score = -d_me * 10 + (d_op - d_me) * 3
        # If moving onto a resource, strongly prefer
        if (nx, ny) in set(tuple(p) for p in resources):
            score += 100000
        # Light tie-break: avoid staying unless it's best
        if (dx, dy) == (0, 0):
            score -= 0.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]