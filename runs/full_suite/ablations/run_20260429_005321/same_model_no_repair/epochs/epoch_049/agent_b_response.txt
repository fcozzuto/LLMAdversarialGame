def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation["grid_width"]
    gh = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_delta = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh):
            continue
        block_pen = -2000 if (nx, ny) in obstacles else 0

        # Our best capture advantage from this next cell
        self_best = -10**18
        opp_best = -10**18
        for rx, ry in resources:
            sd = king_dist(nx, ny, rx, ry)
            od = king_dist(ox, oy, rx, ry)
            # Prefer states where we are relatively closer than opponent.
            v_self = (od - sd) * 120 - sd
            if v_self > self_best:
                self_best = v_self
            # Also punish moves that give opponent a strong relative advantage.
            v_opp = (sd - od) * 120 - od
            if v_opp > opp_best:
                opp_best = v_opp

        # Combined objective: maximize our relative advantage while limiting opponent advantage.
        val = self_best + block_pen - int(0.7 * opp_best)

        # Tie-break: reduce our distance to the nearest resource, then increase distance from opponent.
        if val > best_val:
            best_val = val
            best_delta = [dx, dy]
        elif val == best_val:
            cur_near = min(king_dist(sx, sy, rx, ry) for rx, ry in resources)
            nxt_near = min(king_dist(nx, ny, rx, ry) for rx, ry in resources)
            cur_far = king_dist(sx, sy, ox, oy)
            nxt_far = king_dist(nx, ny, ox, oy)
            if (nxt_near < cur_near) or (nxt_near == cur_near and nxt_far > cur_far):
                best_delta = [dx, dy]

    return best_delta