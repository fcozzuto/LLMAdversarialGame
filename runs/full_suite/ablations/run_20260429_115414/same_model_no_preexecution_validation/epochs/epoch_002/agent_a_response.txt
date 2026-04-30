def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rem = observation.get("remaining_resource_count", len(resources))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                # tie-break deterministically
                key = (max(abs(nx - tx), abs(ny - ty)), dx, dy)
                if best is None or key < best[0]:
                    best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    res_sorted = sorted((int(r[0]), int(r[1])) for r in resources)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_for_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**18
        my_to_opp = cheb(nx, ny, ox, oy)
        # Encourage taking a resource, and also contest those the opponent is near.
        s = 0.0
        contest_weight = 1.25 if rem > 6 else (1.5 if rem > 0 else 0.0)
        opp_weight = 1.0
        for rx, ry in res_sorted:
            d_my = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # closer gets more; if opponent is closer, heavily value contesting it
            gain = 1.0 / (d_my + 1)
            loss = 1.0 / (d_opp + 1)
            if d_opp < d_my:
                s += contest_weight * gain - opp_weight * loss
            else:
                s += gain - 0.6 * loss
            # small extra for immediate pickup
            if d_my == 0:
                s += 2.0
        # Avoid giving opponent easy immediate take by moving too close
        s -= 0.15 * (3 - my_to_opp) if my_to_opp < 3 else 0.0
        return s

    best_mv = [0, 0]
    best_sc = None
    # Deterministic tie-breaking: lower (dx,dy) lex among equals
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            sc = score_for_move(dx, dy)
            if best_sc is None or sc > best_sc or (sc == best_sc and (dx, dy) < (best_mv[0], best_mv[1])):
                best_sc = sc
                best_mv = [dx, dy]
    return best_mv