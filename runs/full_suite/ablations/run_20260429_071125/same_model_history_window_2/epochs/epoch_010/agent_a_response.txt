def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if p is not None)
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal-friendly)

    def step_scores():
        if not resources:
            # Go toward opponent to contest (or stay if blocked)
            best = (10**9, 0, 0)
            for dx, dy in deltas:
                nx, ny = sx + dx, sy + dy
                if not inside(nx, ny):
                    continue
                d = dist(nx, ny, ox, oy)
                key = (d, dx, dy)
                if key < best:
                    best = key
            return best[1], best[2]

        # Choose resource with best "advantage" (we want mydist-odist smallest)
        best_r_key = None
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # tie-break deterministically by coordinates
            key = (myd - od, myd, rx, ry)
            if best_r_key is None or key < best_r_key:
                best_r_key = key
        _, _, tx, ty = best_r_key

        # Evaluate moves by improvement in relative advantage and progress
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            myd2 = dist(nx, ny, tx, ty)
            od2 = dist(ox, oy, tx, ty)
            adv2 = myd2 - od2
            # baseline advantage at current position
            myd0 = dist(sx, sy, tx, ty)
            od0 = dist(ox, oy, tx, ty)
            adv0 = myd0 - od0
            # primary: reduce advantage; secondary: closer to target; tertiary: keep distance from opponent if tie
            val = (adv2, myd2, dist(nx, ny, ox, oy), dx, dy)
            if best is None or val < best:
                best = val
        return best[3], best[4]

    dx, dy = step_scores()
    return [int(dx), int(dy)]