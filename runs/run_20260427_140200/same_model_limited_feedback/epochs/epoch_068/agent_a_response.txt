def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    ax, ay = me[0], me[1]
    bx, by = opp[0], opp[1]

    def dist(p, q):
        return (p[0] - q[0]) * (p[0] - q[0]) + (p[1] - q[1]) * (p[1] - q[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick a target resource that's best relative to opponent reachability
    best_res = None
    best_val = None
    for r in resources:
        rd = dist((ax, ay), r)
        od = dist((bx, by), r)
        val = rd - 0.9 * od  # smaller is better
        if best_val is None or val < best_val or (val == best_val and rd < dist((ax, ay), best_res)):
            best_val = val
            best_res = r

    tx, ty = best_res
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (bx, by):
            continue

        myd = dist((nx, ny), (tx, ty))
        my_now = dist((ax, ay), (tx, ty))
        oppd = dist((nx, ny), (bx, by))
        opp_now = dist((ax, ay), (bx, by))

        # Prefer decreasing distance to target, but also keep/restore separation from opponent
        score = 0.0
        score += (my_now - myd) * 2.0
        score += (oppd - opp_now) * 0.35
        # Avoid stepping onto squares that are "closer" for opponent to the same target
        opp_to_target = dist((bx, by), (tx, ty))
        opp_after = dist((bx, by), (nx, ny))
        score += -0.15 * (opp_after - opp_to_target)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]