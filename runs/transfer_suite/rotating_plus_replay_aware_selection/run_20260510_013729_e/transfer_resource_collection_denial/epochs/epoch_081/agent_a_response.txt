def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal moves)

    if not resources:
        return [0, 0]

    res_set = {(x, y) for x, y in resources}
    if sx == ox and sy == oy:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        immediate = 1 if (nx, ny) in res_set else 0

        # choose target resource that maximizes lead after this move
        best_lead = -10**18
        for rx, ry in resources:
            myd = cd(nx, ny, rx, ry)
            opd = cd(ox, oy, rx, ry)

            # obstacle-aware nudge: if both directions are blocked, penalize
            step_block = 0
            if rx != nx or ry != ny:
                # preferred step toward resource
                sx1 = 0 if rx == nx else (1 if rx > nx else -1)
                sy1 = 0 if ry == ny else (1 if ry > ny else -1)
                if not legal(nx + sx1, ny + sy1):
                    step_block -= 1
                # also try axis step
                if not (legal(nx + sx1, ny) or legal(nx, ny + sy1)):
                    step_block -= 1

            lead = (opd - myd) + step_block
            if lead > best_lead:
                best_lead = lead

        val = 1000 * immediate + best_lead
        # deterministic tie-break: smallest (dx,dy) lexicographically after preferring higher val
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]