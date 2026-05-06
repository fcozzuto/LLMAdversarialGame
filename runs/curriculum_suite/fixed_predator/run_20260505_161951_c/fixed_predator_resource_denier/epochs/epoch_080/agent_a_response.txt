def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def man(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy
    def best_adv(px, py, qx, qy):
        # Advantage for us: (opp closer?) higher means we are better placed to capture.
        best = -10**18
        for rx, ry in resources:
            if not valid(rx, ry):  # should not happen
                continue
            self_d = man(px, py, rx, ry)
            opp_d = man(qx, qy, rx, ry)
            # Prefer cells closer to resources than opponent; also break ties by keeping distance small.
            v = (opp_d - self_d) * 20 - self_d
            # If we can capture immediately, boost strongly.
            if self_d == 0:
                v += 10**6
            best = v if v > best else best
        return best

    if not resources:
        tx, ty = w - 1, h - 1
        best = [0, 0]; bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            v = -man(nx, ny, tx, ty) - cheb(nx, ny, ox, oy) * 0.1
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # One-ply lookahead: we choose our move; opponent greedily chooses their best move next.
    # Score: our advantage minus opponent advantage + small contention term.
    my_best = [0, 0]; my_bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # Opponent greedy step: choose move that maximizes their own ability to capture (negative of ours)
        opp_bestv = -10**18; opp_move = (0, 0)
        for odx, ody in dirs:
            onx, ony = ox + odx, oy + ody
            if not valid(onx, ony):
                continue
            # If opponent captures immediately, it dominates.
            opp_adv = best_adv(onx, ony, nx, ny)
            # Opponent wants to maximize their capture prospects => minimize our advantage
            # Use same function but with swapped roles approximation.
            # Approx: opponent's objective = -best_adv(onx,ony,nx,ny)
            obj = -opp_adv
            if obj > opp_bestv:
                opp_bestv = obj; opp_move = (odx, ody)

        onx, ony = ox + opp_move[0], oy + opp_move[1]
        my_adv = best_adv(nx, ny, onx, ony)
        opp_adv_for_us = best_adv(onx, ony, nx, ny)
        contention = -cheb(nx, ny, onx, ony)  # slight prefer being closer than opponent
        # Also prefer reducing our distance to the best currently-known resource.
        # Estimate by using best resource distance.
        min_self_d = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < min_self_d:
                min_self_d = d
        v = my_adv - 0.85 * opp_adv_for_us + contention - 0.5 * min_self_d

        if v > my_bestv:
            my_bestv = v; my_best = [dx, dy]

    return my_best