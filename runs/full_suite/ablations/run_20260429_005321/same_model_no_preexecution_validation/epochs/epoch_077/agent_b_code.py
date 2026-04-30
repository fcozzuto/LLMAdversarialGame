def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

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

    def near_obs(x, y):
        c = 0
        for ddx, ddy in dirs:
            if (x + ddx, y + ddy) in obstacles:
                c += 1
        return c

    def best_resource_target():
        if not resources:
            return None
        best = None
        bestv = -10**18
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; also account for absolute distance.
            # Add a bias to break ties deterministically by coordinate.
            v = (do - ds) * 3.0 - ds * 0.8 - near_obs(rx, ry) * 0.25
            v += (-rx * 0.001 - ry * 0.0005)
            if v > bestv:
                bestv = v
                best = (rx, ry)
        return best

    target = best_resource_target()
    if target is None:
        # No resources: drift to center while avoiding obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        target = (tx, ty)

    tx, ty = target

    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        # If moving towards the target increases our lead over opponent, prioritize.
        do = cheb(ox, oy, tx, ty)
        ds0 = cheb(sx, sy, tx, ty)
        new_lead = (do - dself)
        old_lead = (do - ds0)
        lead_gain = new_lead - old_lead
        v = -dself * 1.2 + new_lead * 2.2 + lead_gain * 1.0 - near_obs(nx, ny) * 0.6
        # If already at/adjacent, stop.
        if dself == 0:
            v += 5.0
        # Deterministic tie-break: prefer smaller dx, then smaller dy.
        v += -abs(dx) * 0.01 - abs(dy) * 0.005
        if v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]