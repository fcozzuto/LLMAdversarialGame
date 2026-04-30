def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obst = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def adj_obst_pen(x, y):
        pen = 0
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in obst:
                pen += 1
        if x == 0 or x == w - 1 or y == 0 or y == h - 1:
            pen += 0.25
        return pen

    # Pick a resource where we are (currently) ahead, else closest resource.
    if resources:
        best_t = None
        best_ahead = -10**9
        closest = 10**9
        for rx, ry in resources:
            dm = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            ahead = do - dm
            if ahead > best_ahead or (ahead == best_ahead and dm < closest):
                best_ahead = ahead
                closest = dm
                best_t = (rx, ry)
        if best_ahead <= 0:
            # No clear lead: choose closest to us to avoid lagging.
            best_t = min(resources, key=lambda p: cheb(sx, sy, p[0], p[1]))
        tx, ty = best_t
    else:
        # No visible resources: move to center/along diagonal to keep options open.
        tx, ty = (w // 2, h // 2)

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        # If we can pick the target now, heavily prefer it.
        if resources and (nx, ny) in resources:
            val = 10**6
        else:
            d_me = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)  # how close opponent would be if we moved here
            # Advance score: reduce our distance while increasing separation from opponent.
            val = -d_me + 0.35 * d_opp

            # Competition: estimate whether opponent is more likely to reach the same target first.
            # (Opponent's current distance reduced by one turn, ours reduced by one turn via next step.)
            if resources:
                cur_d_opp_to_t = cheb(ox, oy, tx, ty)
                cur_d_me_to_t = cheb(sx, sy, tx, ty)
                my_next = d_me
                opp_next = cur_d_opp_to_t - 1
                if opp_next < 0:
                    opp_next = 0
                val += 0.75 * (opp_next - my_next)

        val -= 1.25 * adj_obst_pen(nx, ny)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]