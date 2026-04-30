def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def obs_near(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    def best_target_score(mx, my):
        if not resources:
            cx, cy = w // 2, h // 2
            return -cheb(mx, my, cx, cy) - 0.25 * obs_near(mx, my) + 0.05 * cheb(ox, oy, cx, cy)
        best = -10**18
        for rx, ry in resources:
            d_me = cheb(mx, my, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier and that are "stolen" by opponent less.
            # Penalize if we're close to obstacles and the resource is far (pathing risk).
            v = 5.0 * (d_op - d_me) - 0.9 * d_me + 0.15 * (d_op) - 0.35 * obs_near(mx, my)
            if v > best:
                best = v
        return best

    # Choose move that maximizes (target advantage) with small tie-breakers:
    # - avoid obstacles
    # - avoid being adjacent to obstacles
    # - prefer moving away from opponent if tie
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        val = best_target_score(nx, ny)
        val -= 0.05 * obs_near(nx, ny)
        # tie-break: slight preference to increase distance from opponent if resources are gone/uncertain
        val += 0.02 * cheb(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]