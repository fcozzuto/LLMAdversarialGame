def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = w // 2, h // 2

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            capture = 1000000 if (nx, ny) in blocked and (nx, ny) in resources else 0
            # (capture can't happen because resources are on valid cells; keep simple bonus)
            capture = 1000000 if (nx, ny) in set(resources) else 0

            best_r = -10**18
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                # Prefer resources where we can arrive earlier than opponent, but still closer overall.
                val = (od - sd) * 50 - sd * 10
                if (nx == rx and ny == ry):
                    val += 100000
                if val > best_r:
                    best_r = val

            score = best_r + capture
        else:
            # No resources: go toward center while moving away from opponent.
            dc = cheb(nx, ny, cx, cy)
            da = cheb(nx, ny, ox, oy)
            score = -dc * 20 + da * 10

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]