def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {tuple(p) for p in observation.get("obstacles", [])}
    resources = [tuple(p) for p in observation.get("resources", [])]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def safe(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def obst_burden(nx, ny):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in obstacles:
                    c += 1
        return c

    best = (0, 0)
    best_val = -10**18
    res_set = set(resources)

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not safe(nx, ny):
            continue

        d_op = cheb(nx, ny, ox, oy)

        if resources:
            # Prefer nearest resource from candidate; tie-break with current distance
            best_d = 10**9
            best_cur = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < best_d or (d == best_d and cheb(x, y, rx, ry) < best_cur):
                    best_d = d
                    best_cur = cheb(x, y, rx, ry)
            dist_term = -best_d
            capture_bonus = 40 if (nx, ny) in res_set else 0
            # If we can reach much sooner than opponent, push harder deterministically
            opp_best = 10**9
            for rx, ry in resources:
                od = cheb(ox, oy, rx, ry)
                if od < opp_best:
                    opp_best = od
            lead = opp_best - best_d
            lead_term = 6 * lead
        else:
            dist_term = 0
            capture_bonus = 0
            lead_term = 0

        # Keep distance from opponent to prevent contesting
        sep_term = 2.5 * d_op
        # Slightly avoid cluttered obstacle-adjacent squares
        clutter_term = -1.2 * obst_burden(nx, ny)

        val = dist_term + capture_bonus + lead_term + sep_term + clutter_term

        if val > best_val:
            best_val = val
            best = (dx, dy)

    # If all moves blocked (unlikely), stay
    return [best[0], best[1]]