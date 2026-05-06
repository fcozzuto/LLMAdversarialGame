def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []

    obs = set()
    for o in obstacles_in:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]
    if not res:
        # stay or move away from opponent deterministically
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            opp_d = abs(nx - ox) + abs(ny - oy)
            key = (-opp_d, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # For each move, choose the best resource to pursue based on "race" advantage.
    # Utility aims to make (opp_d - my_d) large, then keep my_d small.
    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_res_for_move = None
        for rx, ry in res:
            my_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            # Prefer resources where we are closer than opponent (opp_d - my_d bigger).
            # Tie-break by closer my_d, then resource coords.
            key_r = (-(opp_d - my_d), my_d, rx, ry)
            if best_res_for_move is None or key_r < best_res_for_move:
                best_res_for_move = key_r
        # Also mildly prefer moves that reduce distance to opponent less aggressively (avoid useless chase).
        opp_next = abs(nx - ox) + abs(ny - oy)
        move_key = (best_res_for_move, opp_next, dx, dy)
        if best_key is None or move_key < best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]