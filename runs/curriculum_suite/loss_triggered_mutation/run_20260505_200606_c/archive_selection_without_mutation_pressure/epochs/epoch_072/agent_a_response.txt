def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or []) if p is not None and len(p) >= 2}
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Evaluate each move by the best "contestedness" it creates:
    # prefer resources where opponent is relatively far (d_opp - d_our high)
    # and, as tie-break, prefer resources that are absolutely far from opponent (deny-proof).
    best_dx, best_dy = 0, 0
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        best_local = None
        best_farthest_from_opp = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_our = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            diff = d_opp - d_our
            # Guarded preference: only consider resources not currently closer to opponent than us by too much.
            # If all are opponent-closer, diff still drives us to the least bad option.
            guarded = diff >= -1
            key = (1 if guarded else 0, diff, -d_opp, -d_our)
            if best_local is None or key > best_local:
                best_local = key
                best_farthest_from_opp = d_opp
        if best_local is None:
            continue
        # Primary: guardedness then diff; secondary: maximize d_opp (harder for opponent to steal); final: smaller movement penalty.
        move_key = (best_local[0], best_local[1], best_farthest_from_opp, -abs(dx) - abs(dy), -dx, -dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]