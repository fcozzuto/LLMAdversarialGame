def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
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

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def move_value(nx, ny):
        if resources:
            best = -10**9
            for rx, ry in resources:
                dme = cheb(nx, ny, rx, ry)
                dop = cheb(ox, oy, rx, ry)
                # prioritize resources where we can arrive relatively earlier than opponent
                val = (dop - dme) * 1000 - dme
                # also mildly prefer staying closer to already-scheduled targets (center bias)
                cx, cy = (w - 1) / 2, (h - 1) / 2
                val -= int(cheb(nx, ny, int(cx), int(cy)))
                if val > best:
                    best = val
            return best
        # No resources: keep pressure by moving toward center while increasing distance to opponent
        centerx, centery = (w - 1) // 2, (h - 1) // 2
        dcenter = cheb(nx, ny, centerx, centery)
        dopp = cheb(nx, ny, ox, oy)
        return dcenter * -2 + dopp * 1

    best_move = (0, 0)
    best_val = -10**18
    # deterministic tie-break: prefer moves that keep increasing advantage; then lower dme; then lexical dx,dy
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not valid(nx, ny):
            continue
        val = move_value(nx, ny)
        if resources:
            # secondary metrics
            dme = 10**9
            dop_best = -10**9
            for rx, ry in resources:
                dme = min(dme, cheb(nx, ny, rx, ry))
                dop_best = max(dop_best, cheb(ox, oy, rx, ry))
            # combine for tie-break deterministically
            val2 = val * 10 + (dop_best - dme) - dme
        else:
            val2 = val * 10 + cheb(nx, ny, (w - 1)//2, (h - 1)//2)
        if val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    # If all moves blocked (shouldn't happen), stay still
    return [int(best_move[0]), int(best_move[1])]