def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for c in obstacles:
        if c is not None and len(c) >= 2:
            obs.add((int(c[0]), int(c[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    own = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []) if x is not None and y is not None)
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []) if x is not None and y is not None)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose target deterministically: closest unclaimed to opponent, but not too close to us if already surrounded.
    best_target = None
    best_score = -10**18
    for ux, uy in unclaimed:
        if not inb(ux, uy): 
            continue
        if (ux, uy) in obs:
            continue
        d_op = abs(ux - ox) + abs(uy - oy)
        d_me = abs(ux - sx) + abs(uy - sy)
        # Prefer cells that are closer to opponent than to us, and generally reduce distance to opponent.
        s = (d_me <= 1) * -3 + (-(d_op)) + (-0.2 * d_me)
        # slight bias toward edges to avoid opponent "sweep" stabilization
        edge_bias = 0.0
        if ux == 0 or ux == w - 1 or uy == 0 or uy == h - 1:
            edge_bias = 0.15
        s += edge_bias
        if s > best_score:
            best_score = s
            best_target = (ux, uy)

    # If no unclaimed, target the nearest cell in opponent territory (to flip) else toward opponent.
    if best_target is None:
        if opp:
            best_target = min(opp, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        else:
            best_target = (ox, oy)

    tx, ty = best_target
    # Evaluate candidate moves: prefer entering opponent territory (flip), avoid obstacles, reduce distance to target.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        # Capturing heuristics: entering opponent territory is valuable; entering our territory is neutral.
        flip = (nx, ny) in opp
        gain_own = (nx, ny) in own
        # Discourage moving away when close to target.
        val = 0
        val += (20 if flip else 0)
        val += (-0.6 * d_t)
        val += (0.05 * (-d_o))  # slightly press forward toward opponent
        val += (-0.2 if gain_own else 0)
        # Prefer not staying still when target exists.
        if dx == 0 and dy == 0:
            val -= 0.1
        # Deterministic tie-breaker via ordering of moves in dirs.
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move