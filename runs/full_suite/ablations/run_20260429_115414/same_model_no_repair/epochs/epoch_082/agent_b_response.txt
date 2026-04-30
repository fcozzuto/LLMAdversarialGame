def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    opp_d = man(sx, sy, ox, oy)
    best_move = [0, 0]
    best_val = None

    # One-ply lookahead: choose the move that maximizes our best "advantage" over resources.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        cur_best = None
        for rx, ry in resources:
            md = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # We prefer resources where we are closer (md small) and the opponent is farther (od-md large).
            # If we're behind, still choose the least-bad contest.
            val = (od - md) * 3 - md
            if cur_best is None or val > cur_best:
                cur_best = val

        # Add slight pressure to avoid giving the opponent an easy next step near us.
        # (Deterministic, local, and cheap.)
        val2 = cur_best - (opp_d if opp_d else 0)
        if best_val is None or val2 > best_val:
            best_val = val2
            best_move = [dx, dy]

    return best_move if inb(sx + best_move[0], sy + best_move[1]) else [0, 0]