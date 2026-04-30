def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Precompute resource "urgency" from current state
    res_vals = []
    for rx, ry in resources:
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources I can reach no later than opponent, and where I have an advantage.
        # Also slightly prefer nearer resources to speed up scoring.
        val = (do - dm) * 100 - dm
        res_vals.append((val, rx, ry))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        my_d_opp = cheb(nx, ny, ox, oy)
        # Encourage not giving the opponent an immediate capture line.
        # (Opponent capture mechanics are unknown; this is a conservative spacing heuristic.)
        val = -my_d_opp

        # Add gain from moving closer to the best available resource(s)
        for r_base, rx, ry in res_vals:
            dm_new = cheb(nx, ny, rx, ry)
            # If I move closer to a resource where I lead, this increases value.
            # If I move into a resource where I don't lead, it decreases value.
            val += r_base - dm_new + (10 if dm_new <= cheb(ox, oy, rx, ry) else 0)

        # Small preference to actually reduce distance to opponent resources overall
        if resources:
            val += -min(cheb(nx, ny, rx, ry) for rx, ry in resources)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]