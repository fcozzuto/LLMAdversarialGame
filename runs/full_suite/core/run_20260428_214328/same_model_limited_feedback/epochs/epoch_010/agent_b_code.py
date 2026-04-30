def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # fallback: move away from opponent if close, else towards center
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d_to_opp = abs(nx - ox) + abs(ny - oy)
            d_to_ctr = abs(nx - tx) + abs(ny - ty)
            v = d_to_opp * 3.0 + (-d_to_ctr)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # Choose target resource where we are relatively closer than opponent
    best_res, best_key = None, None
    for rx, ry in resources:
        ds = abs(sx - rx) + abs(sy - ry)
        do = abs(ox - rx) + abs(oy - ry)
        # key prefers resources where we can beat opponent and also overall proximity
        key = (do - ds, -ds)
        if best_key is None or key > best_key:
            best_key, best_res = key, (rx, ry)
    rx, ry = best_res

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move, best_val = (0, 0), -10**18
    my_d0 = dist(sx, sy, rx, ry)
    opp_d0 = dist(ox, oy, rx, ry)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = dist(nx, ny, rx, ry)
        d_opp = dist(nx, ny, ox, oy)
        # If we're about to collect (deterministic: cell equals resource position), prioritize strongly
        collect = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0

        # Strategy shift: contest by not letting opponent get closer to the same target.
        opp_to_target = dist(ox, oy, rx, ry)
        # Estimate whether this move reduces our lead vs opponent (higher is better)
        lead_now = (opp_d0 - my_d0)
        lead_next = (opp_to_target - d_self)

        # Scoring: collect > approach target > keep distance from opponent > contest lead > slight center bias
        center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
        d_center = abs(nx - center_x) + abs(ny - center_y)
        val = (collect * 10.0
               + (my_d0 - d_self) * 2.2
               + (lead_next - lead_now) * 1.2
               + d_opp * 0.35
               - d_self * 0.08
               - d_center * 0.01)
        if val > best_val:
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]