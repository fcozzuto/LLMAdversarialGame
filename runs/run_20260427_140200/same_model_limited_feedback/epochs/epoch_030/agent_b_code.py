def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Pick a target resource with deterministic scoring (advantage-first).
    my_best = None
    best_val = -10**9
    for rx, ry in resources:
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        advantage = od - md  # positive if I'm closer
        val = advantage * 6 - md
        if md == 0:
            val = 10**6
        if val > best_val:
            best_val = val
            my_best = (rx, ry)

    if my_best is None:
        return [0, 0]
    tx, ty = my_best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic order above acts as tie-breaker.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)

        if (nx, ny) in obstacles:
            score = -10**12
        else:
            # Move toward target, avoid getting too close to opponent, slightly prefer safe progress.
            d_to_t = dist(nx, ny, tx, ty)
            d_to_o = dist(nx, ny, ox, oy)
            progress = dist(sx, sy, tx, ty) - d_to_t
            # If target is now taken/contested, bias away from opponent.
            score = progress * 25 - d_to_t * 2 + d_to_o * 0.6
            # Extra penalty if next step would reduce opponent-to-target distance (contesting effect).
            if resources:
                contested = 0
                for rx, ry in resources:
                    md2 = dist(nx, ny, rx, ry)
                    od2 = dist(ox, oy, rx, ry)
                    if od2 <= md2:
                        contested += 1
                score -= contested * 3

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]