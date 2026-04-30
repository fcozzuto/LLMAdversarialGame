def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = (float("-inf"), (0, 0))

    if resources:
        # Opponent baseline distances help us choose moves that keep them away from resources.
        d_opp = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            # Maximize: closeness to resources, while keeping opponent farther from them.
            # Add slight term to prefer increasing our distance from opponent.
            val = (-d_self) + 0.5 * d_opp + 0.05 * cheb(nx, ny, ox, oy)
            if val > best[0]:
                best = (val, (dx, dy))
    else:
        # No visible resources: head toward opponent-relevant corner deterministically.
        # Move to increase distance from opponent while staying near center-ish.
        target = (w // 2, h // 2)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            val = cheb(nx, ny, ox, oy) - 0.01 * cheb(nx, ny, target[0], target[1])
            if val > best[0]:
                best = (val, (dx, dy))

    dx, dy = best[1]
    return [int(dx), int(dy)]