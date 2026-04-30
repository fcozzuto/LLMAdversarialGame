def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    try:
        rem = int(observation.get("remaining_resource_count"))
    except:
        rem = len(resources)
    late = rem <= 4

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_obs_pen(x, y):
        if not obstacles:
            return 0
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obstacles:
                    p += 2
        return p

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        our_d_block = cheb(nx, ny, ox, oy)
        step_pen = adj_obs_pen(nx, ny)
        if late:
            # Late: race for nearest resource directly
            score = -min(cheb(nx, ny, rx, ry) for rx, ry in resources) - 0.01 * our_d_block - step_pen
        else:
            # Early/mid: grab "contested" resources where we are relatively closer than opponent
            best_adv = -10**9
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                adv = (od - sd)  # positive means we are closer
                # small secondary: prefer resources also not too far from us
                adv -= 0.02 * sd
                if adv > best_adv:
                    best_adv = adv
            score = best_adv - 0.01 * our_d_block - step_pen

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]) if best else 0, int(best[1]) if best else 0]