def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev with diagonals

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        dx = 0
        dy = 0
        if sx < w-1: dx = 1
        elif sx > 0: dx = -1
        if sy < h-1: dy = 1
        elif sy > 0: dy = -1
        return [dx, dy]

    best_res = None
    best_adv = -10**9
    for r in resources:
        sdist = dist((sx, sy), r)
        odist = dist((ox, oy), r)
        adv = odist - sdist  # prefer resources we are closer to
        if adv > best_adv:
            best_adv = adv
            best_res = r

    if best_adv < 0:
        # no clear advantage: go to nearest resource
        best_res = min(resources, key=lambda r: dist((sx, sy), r))

    tx, ty = best_res
    # If we're already on a resource, prioritize staying (engine likely handles pickup)
    if (sx, sy) == (tx, ty):
        return [0, 0]

    opp_dist = dist((ox, oy), (tx, ty))
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        # progress to target + keep opponent away (soft)
        to_opp = dist((nx, ny), (ox, oy))
        score = (-nd) * 10 + to_opp * 0.3
        # if we can reduce our distance substantially and prevent opponent getting too close
        if opp_dist > 0:
            score += (opp_dist - dist((ox, oy), (tx, ty))) * 0.0
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]