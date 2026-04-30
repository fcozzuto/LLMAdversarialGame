def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    res_set = set(resources)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_dist(x, y, targets):
        if not targets:
            return 10**9
        best = None
        for tx, ty in targets:
            d = cheb(x, y, tx, ty)
            if best is None or d < best:
                best = d
        return best if best is not None else 10**9

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    opp_targets = resources
    my_targets = resources

    my_near_from_opp = nearest_dist(ox, oy, opp_targets)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_my = nearest_dist(nx, ny, my_targets)
        if (nx, ny) in res_set:
            d_my = 0

        d_opp = my_near_from_opp
        if opp_targets:
            d_opp = nearest_dist(ox, oy, opp_targets)

        val = 0
        val -= 3.0 * d_my
        if my_targets:
            if d_my == 0:
                val += 50
            else:
                if dx == 0 and dy == 0:
                    val -= 1.0
        # Competitive pressure: prefer states that are relatively closer than opponent is
        val += 1.5 * (d_opp - d_my)

        # Small deterministic tie-break: prefer moves toward upper-left lexicographically (via dirs order)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]