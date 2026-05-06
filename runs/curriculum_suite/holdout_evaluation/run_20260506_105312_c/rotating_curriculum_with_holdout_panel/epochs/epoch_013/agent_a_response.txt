def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obs_near(x, y):
        c = 0
        for ax, ay in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            nx, ny = x + ax, y + ay
            if (nx, ny) in obstacles:
                c += 1
        return c

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_near_obs = obs_near(nx, ny)
        move_score = -my_near_obs * 0.7  # discourage obstacle-adjacent moves

        for rx, ry in resources:
            myd_before = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            myd_after = cheb(nx, ny, rx, ry)

            # If we can be first (or not much worse), greedily reduce our distance.
            # If opponent is clearly closer, avoid that resource and instead improve
            # the relative margin if possible.
            if myd_after <= opd:
                score = (opd - myd_after) * 2.4 + (myd_before - myd_after) * 1.1
            else:
                score = (opd - myd_after) * 1.7 - (myd_after - myd_before) * 0.6

            # Small bias toward resources that are generally closer to us.
            score += (14 - myd_after) * 0.08
            if (rx, ry) == (nx, ny):
                score += 6.0  # immediate pickup target

            if score > -10**17:
                move_score += score

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]