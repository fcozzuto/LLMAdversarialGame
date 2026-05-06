def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Target selection: prefer resources that are far from opponent (harder for them to reach).
    best_target = None
    best_tx = None
    for rx, ry in resources:
        d_to_opp = man(rx, ry, ox, oy)
        d_to_us = man(rx, ry, sx, sy)
        # Score: prioritize contest by opponent distance, break ties by our distance, then position.
        sc = (d_to_opp * 10 - d_to_us, -min(rx, ry), rx, ry)
        if best_target is None or sc > best_tx:
            best_target = (rx, ry)
            best_tx = sc

    tx, ty = best_target

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        d_us_target = man(nx, ny, tx, ty)
        d_us_opp = man(nx, ny, ox, oy)

        # Also consider the nearest resource from the candidate to avoid getting trapped
        # if target becomes unreachable due to obstacles.
        near_res = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = man(nx, ny, rx, ry)
            if d < near_res:
                near_res = d

        # Main objective: move toward target while maximizing separation from opponent.
        # Add a small deterministic bias toward edges to reduce opponent blocking collisions.
        edge_bias = 0
        if nx in (0, w - 1) or ny in (0, h - 1):
            edge_bias = 0.1

        val = (d_us_opp * 2.5 - d_us_target) + (-0.02 * near_res) + edge_bias

        # Tie-break deterministically: prefer smaller dx, then smaller dy.
        tieb = (-dx, -dy)
        if best_val is None or (val > best_val) or (val == best_val and tieb > (-(best_move[0]), -(best_move[1]))):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]