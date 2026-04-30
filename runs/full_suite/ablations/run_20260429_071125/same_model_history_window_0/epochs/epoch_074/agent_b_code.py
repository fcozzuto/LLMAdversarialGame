def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    myx, myy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    # Pick a target resource that I can reach earlier than opponent, otherwise the least-bad.
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_my = cheb(myx, myy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Key: primary advantage, then closer to me, then prefer higher opponent disadvantage.
        key = (d_op - d_my, -d_my, d_op)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (myx, myy)

    # Candidate moves (including stay), avoid obstacles and keep inside grid.
    deltas = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = myx + dx, myy + dy
        if not valid(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        d_to_opp = cheb(nx, ny, ox, oy)
        # Prefer reducing distance to target; if tied, increase distance from opponent; then prefer moving.
        key = (-d_to_target, d_to_opp, -(abs(dx) + abs(dy)))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    # If no valid moves found (rare if obstacles surround), try any in-bounds non-obstacle else stay.
    if best_move_key is None:
        for dx, dy in deltas:
            nx, ny = myx + dx, myy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]