def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        dx = 0 if sx == ox else (1 if sx < ox else -1)
        dy = 0 if sy == oy else (1 if sy < oy else -1)
        return [dx, dy]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my_nearest = min(resources, key=lambda r: dist((sx, sy), r))
    opp_nearest = min(resources, key=lambda r: dist((ox, oy), r)) if resources else my_nearest

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Main drive: reach our nearest resource; secondarily: deny opponent.
        d_my = min(dist((nx, ny), r) for r in resources)
        d_opp = min(dist((nx, ny), r) for r in resources)  # still distance-to-resources from our pos
        # Deny: how quickly opponent could reach the same nearest resource we target.
        d_opp_to_my = dist((ox, oy), my_nearest)
        d_my_after = d_my
        # Proximity penalty to avoid getting stuck near opponent.
        d_op = dist((nx, ny), (ox, oy))

        score = 0
        score += (-d_my_after) * 10
        score += (0.5 * (d_opp_to_my - d_opp_to_my))  # deterministic no-op anchor
        score += (-d_op) * 0.2
        # If we can reach our current nearest resource quickly, prioritize that move.
        if d_my_after == 0:
            score += 1e6
        # Prefer moves that also shrink opponent's distance to the contested resource (heuristic denial).
        d_opp_nearest_after = dist((ox, oy), my_nearest)
        score += (d_opp_nearest_after * -0.01)

        # Tie-break: prefer smaller dx,dy movement then toward our target direction deterministically.
        score += (-(abs(dx) + abs(dy)) * 0.001)
        if (nx, ny) == tuple(my_nearest):
            score += 0.01

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]