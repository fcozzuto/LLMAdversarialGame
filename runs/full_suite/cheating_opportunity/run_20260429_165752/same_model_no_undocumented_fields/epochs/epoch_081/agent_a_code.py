def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Deterministic dir ordering: prefer towards center then upward-leftish to stabilize ties
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def eval_pos(px, py):
        if (px, py) in obstacles:
            return -10**12
        # Main: pick resource where we have a timing advantage; also bias toward capturing/denying
        if resources:
            best = -10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = cheb(px, py, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer large advantage to beat opponent; slight preference for closer capture
                adv = do - ds
                # If we can reach in 0, prioritize strongly
                cap_bonus = 1000 if ds == 0 else (50 - ds)
                # Deny bonus: even if we can't beat them, discourage targets they are much closer to
                deny = -2 * max(0, ds - do)
                center_bias = -0.1 * cheb(rx, ry, int(cx), int(cy))
                val = 100 * adv + cap_bonus + deny + center_bias
                if val > best:
                    best = val
            return best
        # No resources visible: move toward center while not worsening opponent approach too much
        dc = cheb(px, py, int(cx), int(cy))
        do_center = cheb(ox, oy, int(cx), int(cy))
        return -dc + 0.05 * (do_center - dc)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = eval_pos(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]