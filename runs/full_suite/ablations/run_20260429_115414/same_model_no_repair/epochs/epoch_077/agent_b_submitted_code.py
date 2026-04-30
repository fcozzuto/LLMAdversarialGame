def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((x, y) for x, y in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp_dir(dx, dy):
        if dx < -1: dx = -1
        if dx > 1: dx = 1
        if dy < -1: dy = -1
        if dy > 1: dy = 1
        return dx, dy

    def best_target():
        if not resources:
            return None
        best = None
        best_val = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are not behind; if behind, strongly avoid.
            behind = do - ds
            if behind >= 2:
                val = -10**9 - behind
            else:
                val = (ds - do) * 2  # we want ds<=do => non-positive; invert logic
                val = (-val)  # now prefers ds close to do, with ds<=do best
                # If very close and we can deny, boost; otherwise moderate.
                if ds <= do:
                    val += 6 - ds
                else:
                    val -= (do - ds) * 2
            # Small bias: aim toward our nearer side to reduce travel time.
            val += -0.01 * (abs(rx - 7) + abs(ry - 7))
            # Obstacle interference: penalize resources that are near obstacles.
            if obstacles:
                p = 0
                for ax, ay in obstacles:
                    d = cheb(rx, ry, ax, ay)
                    if d == 0:
                        p += 100
                    elif d == 1:
                        p += 3
                    elif d == 2:
                        p += 1
                val -= p
            if val > best_val:
                best_val = val
                best = (rx, ry)
        return best

    tx = best_target()
    if tx is None:
        return [0, 0]
    rx, ry = tx

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = cheb(nx, ny, rx, ry)
        d_curr = cheb(sx, sy, rx, ry)
        # Must make progress, but allow a small stall if needed for pathing.
        progress = d_curr - d_to_target
        # Avoid stepping near obstacles.
        prox_pen = 0
        if obstacles:
            for ax, ay in obstacles:
                d = cheb(nx, ny, ax, ay)
                if d == 0:
                    prox_pen += 1000
                elif d == 1:
                    prox_pen += 5
                elif d == 2:
                    prox_pen += 1
        # Also reduce chance opponent grabs immediately by moving away when very close to opponent.
        opp_close = cheb(nx, ny, ox