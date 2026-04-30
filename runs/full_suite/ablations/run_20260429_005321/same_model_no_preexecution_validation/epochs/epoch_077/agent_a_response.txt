def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(x), int(y)) for x, y in (observation.get("resources") or [])]
    obstacles = {(int(x), int(y)) for x, y in (observation.get("obstacles") or [])}
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    resset = set(resources)

    def near_obs_score(x, y):
        c = 0
        for ddx, ddy in dirs:
            if (x + ddx, y + ddy) in obstacles:
                c += 1
        return c

    def pick_target():
        if not resources:
            return (w // 2, h // 2)
        best_t, best_v = resources[0], -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer targets where we are closer; also prefer closer ones to reduce time.
            v = (d_op - d_me) * 2.5 - 0.35 * d_me - 0.08 * near_obs_score(rx, ry)
            if (rx, ry) in resset:
                v += 0.5
            if v > best_v:
                best_v, best_t = v, (rx, ry)
        return best_t

    tx, ty = pick_target()
    bestm, bestv = (0, 0), -10**18
    d_op_to_t = cheb(ox, oy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_me_to_t = cheb(nx, ny, tx, ty)
        # Encourage getting closer and denying opponent by being earlier.
        v = (d_op_to_t - d_me_to_t) * 2.2 - 0.25 * d_me_to_t - 0.35 * near_obs_score(nx, ny)
        if (nx, ny) in resset:
            v += 50.0
        if v > bestv:
            bestv, bestm = v, (dx, dy)

    return [int(bestm[0]), int(bestm[1])]