def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                cur = -10**9
                for rx, ry in resources:
                    sd = cheb(nx, ny, rx, ry)
                    od = cheb(ox, oy, rx, ry)
                    val = (-sd) + 0.8 * od
                    if val > cur:
                        cur = val
                # small tiebreak: prefer increasing distance from opponent
                cur += 0.02 * cheb(nx, ny, ox, oy)
                if cur > best_val:
                    best_val = cur
                    best_move = (dx, dy)
    else:
        # no resources seen: spread from opponent while avoiding obstacles
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                cur = cheb(nx, ny, ox, oy)
                if cur > best_val:
                    best_val = cur
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]