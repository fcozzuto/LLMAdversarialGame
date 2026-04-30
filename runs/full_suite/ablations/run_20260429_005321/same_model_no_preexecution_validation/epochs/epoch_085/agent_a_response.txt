def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def adj_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    if resources:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            v = (dop - dme) * 10.0 - dme * 0.6 - adj_obs(rx, ry) * 1.3
            # small deterministic bias to break ties consistently
            v += -0.01 * (rx + 2 * ry)
            if v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w // 2, h // 2)

    # If we can take a resource immediately, do it.
    for rx, ry in resources:
        if cheb(sx, sy, rx, ry) == 0:
            tx, ty = rx, ry
            break

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dme2 = cheb(nx, ny, tx, ty)
        dop2 = cheb(ox, oy, tx, ty)
        # Prefer being earlier than opponent at the target; also avoid "trap" squares near obstacles
        score = (dop2 - dme2) * 12.0 - dme2 * 1.0 - adj_obs(nx, ny) * 1.6
        # If stepping onto a resource, huge bonus
        if (nx, ny) in resources:
            score += 10**9
        # Slightly prefer moving generally toward center to reduce dead-ends
        score += -0.02 * cheb(nx, ny, w // 2, h // 2)
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]