def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", None)
    if resources is None:
        resources = []
    else:
        resources = resources or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((int(r[0]), int(r[1])))

    if targets:
        tx, ty = min(targets, key=lambda t: cheb(sx, sy, t[0], t[1]))
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        opp_d = cheb(nx, ny, ox, oy)
        # If chasing a target resource, also lightly prefer staying away from opponent.
        # If no resources, chasing opponent (still keep some safety).
        if targets:
            val = (d, -opp_d)
        else:
            val = (d, opp_d)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if legal(sx + best_move[0], sy + best_move[1]):
        return [int(best_move[0]), int(best_move[1])]
    # Fallback: find any legal move deterministically
    for dx, dy in moves:
        if legal(sx + dx, sy + dy):
            return [int(dx), int(dy)]
    return [0, 0]