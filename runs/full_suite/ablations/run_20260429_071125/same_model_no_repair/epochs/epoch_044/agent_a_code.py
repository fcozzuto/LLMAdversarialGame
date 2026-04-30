def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def viable_target(rt):
        rx, ry = rt
        if (rx, ry) in obstacles:
            return False
        return True

    # Pick a target set prioritized by "we are not too far behind".
    best_target = None
    best_tkey = None
    for rx, ry in resources:
        if not viable_target((rx, ry)):
            continue
        us = cheb(sx, sy, rx, ry)
        op = cheb(ox, oy, rx, ry)
        # If opponent is significantly closer, deprioritize; otherwise race.
        behind_pen = 0
        if op - us >= 2:
            behind_pen = 1000
        # Deterministic tie-break by position.
        key = (behind_pen, us, -(op - us), rx * 8 + ry)
        if best_tkey is None or key < best_tkey:
            best_tkey = key
            best_target = (rx, ry)
    if best_target is None:
        best_target = tuple(resources[0])
    tx, ty = best_target

    # Evaluate next moves: (1) reduce our distance to target, (2) avoid moves that allow opponent to reach target faster,
    # (3) add mild preference to increase distance between agents.
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_d = cheb(nx, ny, tx, ty)
        op_d_now = cheb(ox, oy, tx, ty)
        # If we move away so opponent is now at/near take range relative to us, penalize.
        # (Opponent can also move, approximate by using one-step gain bound: -1 in Chebyshev.)
        op_d_after = max(0, op_d_now - 1)
        rel = op_d_after - our_d
        # rel < 0 is good for us (we are closer); penalize if rel >= 0.
        rel_pen = 0 if rel < 0 else (10 + rel * 3)
        gap = cheb(nx, ny, ox, oy)
        # Slightly prefer to keep distance from opponent to reduce contested grabs.
        key = (rel_pen, our_d, -gap, nx * 8 + ny)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]