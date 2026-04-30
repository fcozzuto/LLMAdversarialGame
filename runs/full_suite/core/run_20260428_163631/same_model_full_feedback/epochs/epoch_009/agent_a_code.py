def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs2 = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    # Pick a resource where we can arrive no later than the opponent, else contest the closest opponent.
    best = None
    bx = by = None
    for rx, ry in resources:
        if not safe(rx, ry):
            continue
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer "won" resources; if none, prefer the smallest opponent advantage we can still steal.
        if od >= md:
            key = (0, -(od - md), md, rx, ry)
        else:
            key = (1, (od - md), md, rx, ry)
        if best is None or key < best:
            best = key
            bx, by = rx, ry

    if bx is None:
        # No reachable resources: maximize distance from opponent while staying safe.
        best_move = (0, 0)
        best_val = None
        for dx, dy in dirs2:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny):
                continue
            val = (-cheb(nx, ny, ox, oy), cheb(nx, ny, sx, sy), dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Move greedily toward chosen target, but keep away from opponent in ties.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        reach = cheb(nx, ny, bx, by)
        dist_opp = cheb(nx, ny, ox, oy)
        # primary: minimize distance to target; secondary: maximize opponent distance; tertiary: deterministic tie-break.
        key = (reach, -dist_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]