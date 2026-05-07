def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = int(observation.get("grid_width", 8))
    gh = int(observation.get("grid_height", 8))
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def clamp_in(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < gw and 0 <= py < gh:
                obs.add((px, py))

    resources_in = observation.get("resources") or []
    resources = []
    for r in resources_in:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obstacle(nx, ny):
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obs:
                    return 1
        return 0

    # Prefer moves that let us reach a resource while the opponent can't reach it sooner.
    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny) or (nx, ny) in obs:
            continue
        val = -8 * near_obstacle(nx, ny)

        # Encourage stepping toward resources, but strongly avoid ones opponent can beat.
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            if myd == 0:
                val += 300.0
            else:
                val += 60.0 / (1.0 + myd)

            opd = cheb(ox, oy, rx, ry)
            # If opponent is closer, the resource is likely lost; dampen.
            diff = opd - myd
            if diff > 0:
                val -= 85.0 * diff
            elif diff == 0:
                val -= 18.0

            # Mildly prioritize resources with fewer obstacles nearby (safer paths).
            safe = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if (rx + ax, ry + ay) in obs:
                        safe -= 1
            val += 2.5 * safe

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]