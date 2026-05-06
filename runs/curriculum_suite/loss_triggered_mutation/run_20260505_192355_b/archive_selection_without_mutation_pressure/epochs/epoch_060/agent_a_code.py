def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def md(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax + ay

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # pick a small deterministic subset of resources: the 4 closest to us (by manhattan)
    rs = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        rs.append((md(sx, sy, rx, ry), rx, ry))
    rs.sort()
    top = rs[:4]
    if not top:
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # If we are exactly on a resource, strongly prefer to stay/move to it (engine likely handles pickup)
        on_res = 0
        for _, rx, ry in top:
            if nx == rx and ny == ry:
                on_res = 1
                break

        # Advantage = (op closer?) by evaluating resource contest after this move
        score = 0
        my_near = 10**9
        opp_near = 10**9
        for _, rx, ry in top:
            myd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)
            if myd < my_near:
                my_near = myd
            if oppd < opp_near:
                opp_near = oppd
            score += (oppd - myd)
            # small bonus for being able to arrive no later than opponent
            if myd <= oppd:
                score += 1

        # If we can't improve, prefer reducing our distance to the nearest resource
        # and avoid getting too close to opponent when it doesn't help
        opp_dist_now = md(nx, ny, ox, oy)
        score += on_res * 50
        score += -0.1 * my_near
        score += 0.02 * (opp_dist_now - opp_near)

        # Deterministic tie-break
        cand = (score, -my_near, opp_dist_now, dx, dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]