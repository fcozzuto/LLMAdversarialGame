def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = (0, 0, -10**18)
    res = resources
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        my_to_opp = cheb(nx, ny, ox, oy)
        center_bias = -0.02 * (abs(nx - (W - 1) / 2.0) + abs(ny - (H - 1) / 2.0))

        if not res:
            val = -0.1 * my_to_opp + center_bias
        else:
            # Prefer resources where I'm closer; if none, lean toward resources the opponent is close to.
            best_gain = -10**18
            for tx, ty in res:
                dme = cheb(nx, ny, tx, ty)
                dop = cheb(ox, oy, tx, ty)
                # advantage: negative means opponent closer
                advantage = dop - dme
                # strongly reward grabbing/approaching my advantage; otherwise reduce opponent access
                gain = 0.95 * advantage - 0.12 * dme
                # if I'm not closer, still consider reducing opponent's next step by approaching that resource
                if advantage < 0:
                    gain = -0.45 * cheb(nx, ny, tx, ty) + 0.08 * advantage
                if gain > best_gain:
                    best_gain = gain

            # Avoid giving the opponent immediate adjacent control when we're tied on resources.
            # (Deterministic small penalty for proximity to opponent.)
            avoid_opp = -0.08 * max(0, 2 - my_to_opp)
            val = best_gain + avoid_opp + center_bias

        # Deterministic tie-break by move order
        if val > best[2]:
            best = (dx, dy, val)

    return [int(best[0]), int(best[1])]