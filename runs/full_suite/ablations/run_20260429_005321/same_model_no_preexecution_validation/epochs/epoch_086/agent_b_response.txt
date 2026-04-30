def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obs(x, y):
        c = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    def best_target():
        if resources:
            best = None
            bestv = -10**18
            any_win = False
            for rx, ry in resources:
                dme = cheb(sx, sy, rx, ry)
                dop = cheb(ox, oy, rx, ry)
                v = (dop - dme) - 0.25 * dme - 1.0 * adj_obs(rx, ry)
                if dme < dop:
                    any_win = True
                    v += 2.0
                if (any_win and dme >= dop):
                    v -= 0.5
                v += -0.01 * (rx + 3 * ry)  # deterministic tie-break
                if v > bestv:
                    bestv = v
                    best = (rx, ry)
            return best
        return (w // 2, h // 2)

    tx, ty = best_target()

    # Choose safest step toward target; never intentionally step into obstacles.
    best_move = (0, 0)
    bestv = -10**18
    found = False
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        found = True
        dnew = cheb(nx, ny, tx, ty)
        dopp = cheb(ox, oy, nx, ny)  # small bias to move where opponent isn't close
        v = -dnew - 0.8 * adj_obs(nx, ny) + 0.05 * dopp
        v += -0.001 * (dx * dx + 2 * dy * dy)  # deterministic preference
        if v > bestv:
            bestv = v
            best_move = (dx, dy)

    if not found:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]