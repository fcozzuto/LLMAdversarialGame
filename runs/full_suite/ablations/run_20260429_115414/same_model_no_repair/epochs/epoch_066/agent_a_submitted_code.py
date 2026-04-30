def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def passable(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Prefer to stay when surrounded/blocked
    if len(resources) == 0:
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if passable(nx, ny):
                # drift toward top-left if we are on/near bottom-right, else toward bottom-right
                tx, ty = (w - 1, h - 1) if (sx + sy) < (w + h - 2) else (0, 0)
                return [0 if tx == nx else (1 if tx > nx else -1), 0 if ty == ny else (1 if ty > ny else -1)]
        return [0, 0]

    # Precompute resource "priority": inverse of opponent distance, and closeness to our start
    res_info = []
    for rx, ry in resources:
        od = cheb(ox, oy, rx, ry)
        sd = cheb(sx, sy, rx, ry)
        # If opponent is close, we must contest; if we are close, we should sprint.
        # Smaller values mean closer; convert into positive weights.
        opp_need = 0
        if od <= 2:
            opp_need = 9000
        elif od <= 3:
            opp_need = 5000
        elif od <= 4:
            opp_need = 2200
        else:
            opp_need = 900 // (1 + od)
        my_push = 3200 // (1 + sd)
        res_info.append((rx, ry, od, sd, opp_need + my_push))

    def move_barriers(x, y):
        # Penalize moves that step adjacent to obstacles more than necessary (proxy for trapping)
        cnt = 0
        for ddx, ddy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + ddx, y + ddy
            if in_bounds(nx, ny) and (nx, ny) in obstacles:
                cnt += 1
        return cnt

    best_move = [0, 0]
    best_val = -10**18

    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not passable(nx, ny):
            continue

        val = 0
        barrier_pen = move_barriers(nx, ny)
        val -= 60 * barrier_pen

        # Determine which single resource to optimize for, but based on move-relative contest.
        # This is faster than full search and remains deterministic.
        for rx, ry, od, sd0, priority in res_info:
            our_d = cheb(nx, ny, rx, ry)
            lead = od - our_d  # positive if we get closer than opponent at the resource

            # Contest term: strongly prefer being closer, especially when opponent is already close.
            if lead > 0:
                val += (priority // 10) + 2600 * lead // (1 + our_d)
            else:
                # If we are not closer, avoid wasting time unless the resource is still best overall.