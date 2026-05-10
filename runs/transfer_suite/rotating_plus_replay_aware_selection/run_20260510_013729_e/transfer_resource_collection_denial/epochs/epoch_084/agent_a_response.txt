def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Choose opponent's target greedily (deterministic) with obstacle-aware step
    def nearest_res_dist(ax, ay):
        best = 10**9
        for rx, ry in resources:
            d = man(ax, ay, rx, ry)
            if d < best:
                best = d
        return best

    def greedy_step(ax, ay, tx, ty):
        bestd = 10**9
        best = (ax, ay)
        for mdx, mdy in moves:
            nx, ny = ax + mdx, ay + mdy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (nx, ny)
        return best

    # Pick opponent target as the resource minimizing distance, tie by coords
    tx, ty = resources[0]
    best = (man(ox, oy, tx, ty), tx, ty)
    for rx, ry in resources[1:]:
        cand = (man(ox, oy, rx, ry), rx, ry)
        if cand < best:
            best = cand
            tx, ty = rx, ry

    # Evaluate our legal next moves by one-step lookahead
    best_score = -10**18
    best_move = (0, 0)
    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not legal(nsx, nsy):
            nsx, nsy = sx, sy
            mdx, mdy = 0, 0
        nox, noy = greedy_step(ox, oy, tx, ty)
        # Heuristic: maximize (opp-nearest - my-nearest) and progress toward that nearest
        my_near = 10**9
        opp_near = 10**9
        my_prog = 0
        for rx, ry in resources:
            d1 = man(nsx, nsy, rx, ry)
            if d1 < my_near:
                my_near = d1
                my_prog = man(sx, sy, rx, ry) - d1
            d2 = man(nox, noy, rx, ry)
            if d2 < opp_near:
                opp_near = d2
        # Also add a small denial term: staying closer to opponent's target resource than they are
        denial = man(nox, noy, tx, ty) - man(nsx, nsy, tx, ty)
        score = (opp_near - my_near) * 100 + my_prog * 10 + denial
        if score > best_score:
            best_score = score
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]