def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        best = (0, (0, 0))
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            v = -max(abs(nx - ox), abs(ny - oy))
            if v > best[0]:
                best = (v, (dx, dy))
        return [best[1][0], best[1][1]]

    def king_dist(a, b, c, d):
        da = abs(a - c); db = abs(b - d)
        return da if da > db else db

    bestv = -10**18
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        v = 0.0
        opp_to_me = king_dist(nx, ny, ox, oy)
        v -= 0.15 * opp_to_me  # mild: avoid getting too close while contesting

        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            opd = king_dist(ox, oy, rx, ry)
            if myd == 0:
                v += 1200  # decisive pick
            else:
                v += (opd - myd) * 12.0  # win contest
                v -= myd * 1.8          # prefer nearer

        # small wall/obstacle avoidance: keep toward open space
        free = 0
        for adx, ady in [(1,0),(-1,0),(0,1),(0,-1)]:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                free += 1
        v += free * 0.25

        if v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]