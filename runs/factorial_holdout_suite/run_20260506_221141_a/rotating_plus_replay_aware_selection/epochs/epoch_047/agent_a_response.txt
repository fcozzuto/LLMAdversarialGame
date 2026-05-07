def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources: drift to center-ish but avoid obstacles.
    if not resources:
        tx = (gw - 1) // 2
        ty = (gh - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_score = -10**18

    # Evaluate each move by potential resource secured and safety (avoid giving opponent closer access).
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue

        move_score = -0.2 * cheb(nx, ny, ox, oy)  # slight keep-away
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)

            # Prefer taking resources we can reach first or tie-break earlier.
            # Also give extra value for "next-step pickup" if standing on resource.
            if (nx, ny) == (rx, ry):
                rel = 5.0
            else:
                rel = 0.0

            if d_me < d_op:
                rel += 3.0 + 1.0 / (1 + d_me)
            elif d_me == d_op:
                rel += 1.5 + 1.0 / (1 + d_me)
            else:
                rel -= 2.5 + 0.5 / (1 + d_me)  # likely losing it; discourage

            # Encourage moving towards resources that are closer than others (relative focus).
            rel += 0.2 / (1 + d_me)

            move_score += rel

        if move_score > best_score:
            best_score = move_score
            best_move = [dxm, dym]

    return best_move