def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    rset = set((r[0], r[1]) for r in resources)

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx if dx >= 0 else -dx + (dy if dy >= 0 else -dy)

    # fix manhattan with no precedence bug
    def man2(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue

        best_diff = -10**18
        best_selfd = 10**18
        best_optd = 10**18
        best_rx, best_ry = None, None

        for rx, ry in resources:
            myd = man2(nx, ny, rx, ry)
            opd = man2(ox, oy, rx, ry)
            diff = opd - myd
            if diff > best_diff or (diff == best_diff and (myd < best_selfd or (myd == best_selfd and opd < best_optd))):
                best_diff = diff
                best_selfd = myd
                best_optd = opd
                best_rx, best_ry = rx, ry

        # main objective: be closer than opponent to valuable nearby resources
        val = best_diff * 100 - best_selfd
        # immediate pickup bonus
        if (nx, ny) in rset:
            val += 5000
        # discourage moves that let opponent get even closer to its nearest resource
        opp_near = 10**18
        for rx, ry in resources:
            od = man2(ox, oy, rx, ry)
            if od < opp_near:
                opp_near = od
        # if our move is toward the same "best" resource, slightly safer
        if best_rx is not None:
            toward = 0
            if best_rx > nx:
                toward += 1
            elif best_rx < nx:
                toward += 1
            if best_ry > ny:
                toward += 1
            elif best_ry < ny:
                toward += 1
            val += 3 * toward

        # deterministic tie-break: prefer smaller |dx|+|dy| then lexicographic
        dist = abs(dx) + abs(dy)
        if val > best_val or (val == best_val and (dist < abs(best_move[0]) + abs(best_move[1]) or (dist == abs(best_move[0]) + abs(best_move[1]) and (dx, dy) < best_move))):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]