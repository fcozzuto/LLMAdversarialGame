def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if (sx, sy) not in obstacles:
        pass
    else:
        return [0, 0]

    target = (ox, oy)
    best = None
    if resources:
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we're not behind; otherwise fall back to closest.
            behind = myd - opd
            if best is None:
                best = (behind, myd)
                target = (rx, ry)
            else:
                if myd <= opd:
                    if best[0] > 0 or behind < best[0] or (behind == best[0] and myd < best[1]):
                        best = (behind, myd)
                        target = (rx, ry)
                else:
                    if best[0] > 0:
                        if behind < best[0] or (behind == best[0] and myd < best[1]):
                            best = (behind, myd)
                            target = (rx, ry)
                    else:
                        # currently best is a non-behind target; keep it
                        pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd = cheb(nx, ny, target[0], target[1])
        opd = cheb(nx, ny, ox, oy)
        # Maximize: get closer to target, slightly prefer staying away from opponent.
        val = (-myd * 10) + (opd // 3)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]