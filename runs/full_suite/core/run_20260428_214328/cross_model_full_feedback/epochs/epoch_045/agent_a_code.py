def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # If no resources, drift toward opponent's corner to force contact/denial by proximity
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obst:
                val = cheb(nx, ny, ox, oy)
                if best_val is None or val < best_val:
                    best_val = val
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue

        # pick the resource that we can reach best from this move
        best_r = None
        best_selfd = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if best_selfd is None or d < best_selfd:
                best_selfd = d
                best_r = (rx, ry)

        rx, ry = best_r
        oppd = cheb(ox, oy, rx, ry)

        # Contest heuristic: prefer moves where we arrive earlier than the opponent
        # Also discourage late starts and unnecessary wandering.
        val = (oppd - best_selfd) - 0.25 * best_selfd
        if oppd <= best_selfd:
            val -= 1000  # hard discourage contested grabs

        # Small tie-breaker toward reducing chebyshev distance to opponent (strategic pressure)
        val -= 0.01 * cheb(nx, ny, ox, oy)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]