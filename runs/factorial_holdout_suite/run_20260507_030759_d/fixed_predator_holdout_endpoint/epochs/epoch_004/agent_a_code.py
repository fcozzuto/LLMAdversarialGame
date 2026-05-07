def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a target that we can reach earlier than the opponent (ignoring obstacles).
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer bigger lead, then shorter self distance, then stable ordering.
        key = (od - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]

    rx, ry = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    # Potential-field step: go toward target; keep opponent farther from target; avoid proximity.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        opp_to_agent = cheb(nx, ny, ox, oy)

        # Want small self_d, large opp_d, and avoid standing too close to opponent.
        score = (self_d * 3) - (opp_d * 2) + (0 if opp_to_agent >= 2 else 5 + (2 - opp_to_agent))
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
        # Deterministic tie-break
        elif score == best_score:
            if [dx, dy] < best_move:
                best_move = [dx, dy]

    return best_move