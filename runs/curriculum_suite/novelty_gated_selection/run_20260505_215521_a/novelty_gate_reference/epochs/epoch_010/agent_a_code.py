def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = -cheb(nx, ny, cx, cy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Our preferred target: closest to us (Chebyshev)
    best_self = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
    txs, tys = best_self
    # Opponent preferred target: closest to opponent (Chebyshev)
    best_opp = min(resources, key=lambda p: (cheb(ox, oy, p[0], p[1]), p[0], p[1]))
    txo, tyo = best_opp

    def greedy_step(px, py, targetx, targety):
        best = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, targetx, targety)
            # tie-break deterministically toward increasing x, then y
            t = (d, nx, ny)
            if best is None or t < best[0]:
                best = (t, dx, dy)
        return (px, py) if best is None else (px + best[1], py + best[2])

    opp_after = greedy_step(ox, oy, txo, tyo)
    opnx, opny = opp_after

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Encourage progress to our target
        d_self = cheb(nx, ny, txs, tys)
        # Anticipate opponent step; reward states where we are closer to their landing zone
        landing = cheb(nx, ny, opnx, opny)
        # Reward/penalize blocking by being adjacent or on same line-ish (Chebyshev)
        block = -cheb(opnx, opny, nx, ny)
        # Also discourage giving opponent an even easier path to its target
        opp_next_for_this = greedy_step(ox, oy, txo, tyo)
        opp_d = cheb(opp_next_for_this[0], opp_next_for_this[1], txo, tyo)

        score = (-d_self) + 0.35 * block + 0.08 * (-landing) + 0.01 * (-opp_d)
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]