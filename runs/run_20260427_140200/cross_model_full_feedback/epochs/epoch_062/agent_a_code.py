def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose best move by deterministic 1-step lookahead: compete for nearest resource.
    best_move = (0, 0)
    best_val = -10**18

    has_res = len(resources) > 0
    opp_dist_opp_self = cheb(ox, oy, sx, sy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        val = 0

        if has_res:
            # Find best resource target for this move using opponent race.
            best_r = None
            best_r_val = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # prefer resources where we are closer than opponent
                r_val = (opd - myd) * 20 - myd
                # slight preference for nearer resources overall
                if myd < 1:
                    r_val += 1000
                if r_val > best_r_val:
                    best_r_val = r_val
                    best_r = (rx, ry)
            val += best_r_val

            # avoid moves that let opponent get much closer to the target we pick
            if best_r is not None:
                rx, ry = best_r
                val -= cheb(nx, ny, rx, ry) * 2
        else:
            # No resources: go toward center while keeping distance from opponent.
            cx = (w - 1) / 2.0
            cy = (h - 1) / 2.0
            dist_center = abs(nx - cx) + abs(ny - cy)
            val += -dist_center
            val += cheb(nx, ny, ox, oy) * 3

        # minor tie-breakers to be stable and not oscillate: prefer reducing distance to opponent if it helps block
        val += (cheb(nx, ny, ox, oy) - opp_dist_opp_self) * 0.1

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]