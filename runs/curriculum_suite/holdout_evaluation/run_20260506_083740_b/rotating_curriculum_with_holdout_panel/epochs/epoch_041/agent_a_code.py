def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cell_score(cx, cy):
        # Prefer resources where we have advantage; if none, prefer those far from opponent.
        best = None
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            d_me = md(cx, cy, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            adv = d_opp - d_me  # positive => we are closer
            # Center bias to reduce drift on sweep-like patterns
            center = -(abs(rx - (w // 2)) + abs(ry - (h // 2))) * 0.01
            val = adv + center
            if best is None or val > best:
                best = val
        if best is None:
            # No resources: hold toward center but not into obstacles
            return -(abs(cx - (w // 2)) + abs(cy - (h // 2)))
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Look one step: maximize our next advantage, and avoid moving closer to opponent too much.
        v = cell_score(nx, ny)
        opp_close_pen = 0.02 * md(nx, ny, ox, oy)
        # Small preference for progressing away from current corner-stall: toward best resource implicitly
        v -= opp_close_pen
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]