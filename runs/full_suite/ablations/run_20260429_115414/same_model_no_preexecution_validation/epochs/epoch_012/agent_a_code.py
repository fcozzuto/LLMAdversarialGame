def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((int(p[0]), int(p[1])) for p in obstacles)
    x = int(sx); y = int(sy); ox = int(ox); oy = int(oy)

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick target resource: prefer ones we are closer to; if contested, prefer ones they are also not too close to.
    best_res = None
    best_val = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Higher is better
        val = (od - sd) * 1000 - sd
        if best_res is None or val > best_val or (val == best_val and (rx, ry) < best_res):
            best_val = val
            best_res = (rx, ry)

    # If no resources, just hold position
    if best_res is None:
        return [0, 0]

    tx, ty = best_res
    cur_to_op = cheb(x, y, ox, oy)
    cur_to_t = cheb(x, y, tx, ty)

    def near_obstacle_pen(px, py):
        if not obstacles:
            return 0
        dmin = 10**9
        for ax, ay in obstacles:
            d = cheb(px, py, int(ax), int(ay))
            if d < dmin:
                dmin = d
                if dmin == 0:
                    return 10**7
        if dmin == 0:
            return 10**7
        if dmin == 1:
            return 60
        if dmin == 2:
            return 18
        if dmin == 3:
            return 6
        return 0

    # Evaluate candidate moves
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        dt = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)

        # Encourage moving toward target; discourage stepping onto obstacles' vicinity; avoid getting too close to opponent.
        score = dt * 10 + near_obstacle_pen(nx, ny)
        score += (do < cur_to_op) * (cur_to_op - do) * 8

        # If we would arrive at the target, strongly prefer it.
        if dt == 0:
            score -= 100000

        # Tie-break deterministically by direction order (already fixed), then position
        if best_score is None or score < best_score or (score == best_score and (nx, ny) < (x + best_move[0], y + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    # If all moves were blocked (rare), stay put
    return [int(best_move[0]), int(best_move[1])]