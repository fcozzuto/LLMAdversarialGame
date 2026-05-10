def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Deterministic move ordering (diagonals last to reduce accidental corner cutting)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Precompute for quick heuristic
    unclaimed_list = list(unclaimed)
    any_unclaimed = bool(unclaimed_list)

    best = None
    best_sc = -10**9

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        sc = 0.0
        if (nx, ny) in selfT:
            sc += 0.6
        elif (nx, ny) in unclaimed:
            sc += 2.4
        elif (nx, ny) in oppT:
            sc += 1.2  # flipping possible, but generally riskier

        # Gain control by expanding near unclaimed
        adj_unclaimed = 0
        adj_opp = 0
        for ax, ay in neigh4:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty):
                if (tx, ty) in unclaimed:
                    adj_unclaimed += 1
                if (tx, ty) in oppT:
                    adj_opp += 1

        sc += 0.8 * adj_unclaimed
        sc -= 1.35 * adj_opp

        # Strategic direction: move toward the closest unclaimed, but also keep some distance from opponent
        if any_unclaimed:
            d_un = 999
            for ux, uy in unclaimed_list:
                d = man(nx, ny, ux, uy)
                if d < d_un:
                    d_un = d
                    if d_un == 0:
                        break
            sc += 1.0 / (1 + d_un)
        d_opp = man(nx, ny, ox, oy)
        sc += 0.05 * d_opp

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best