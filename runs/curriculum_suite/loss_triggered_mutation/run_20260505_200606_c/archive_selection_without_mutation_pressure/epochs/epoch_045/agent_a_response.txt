def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    parity = observation.get("turn_index", 0) & 1
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target where we have a meaningful closeness advantage; otherwise contest center.
    best = None
    best_key = None
    cx, cy = w // 2, h // 2
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # We want ds < do; if not possible, we won't pick it.
        if ds < do - 0.5:
            adv = (do - ds)
            # Tie-break deterministically: earlier in scan, then parity bias
            key = (-adv, (rx + ry + parity) % 2, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)

    if best is None:
        tx, ty = (cx + (parity * 1 - 0)) if in_bounds(cx + (parity * 1 - 0), cy) else cx, cy
    else:
        tx, ty = best

    # Choose move that most reduces distance to chosen target, with obstacle avoidance and slight opponent pressure.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer closer to our target; discourage moving adjacent-far from it. Also deterministic tie-break.
        val_key = (d_self, -d_opp, (nx + ny + parity) % 2, dx, dy)
        if best_val is None or val_key < best_val:
            best_val = val_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]