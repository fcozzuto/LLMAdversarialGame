def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target_distance(x, y):
        if not resources:
            return 10**9
        return min(man(x, y, rx, ry) for rx, ry in resources)

    cur_res_d = best_target_distance(sx, sy)
    cur_opp_d = man(sx, sy, ox, oy)

    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        opp_d = man(nx, ny, ox, oy)
        res_d = best_target_distance(nx, ny)

        # Two-step "commitment": estimate next best improvement without full search
        best_next = 10**9
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if not inb(tx, ty) or not ok(tx, ty):
                continue
            d2 = best_target_distance(tx, ty)
            if d2 < best_next:
                best_next = d2

        gain_res_now = cur_res_d - res_d
        gain_res_next = res_d - best_next
        opp_pen = cur_opp_d - opp_d  # positive if opponent gets closer (bad for us)

        # If resources exist, strongly prefer moves that reduce resource distance.
        # Also avoid moves that bring us too near the opponent unless it also helps resources a lot.
        score = (gain_res_now * 10) + (gain_res_next * 3) - (opp_pen * 6)
        if resources:
            score += (opp_d >= cur_opp_d and 2 or -1)
        else:
            # No resources: spread from opponent deterministically
            score += (opp_d - cur_opp_d) * 5

        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [best[1], best[2]]