def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    resources = [tuple(r) for r in observation.get("resources", []) or []]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = -10**18
    near_res = None
    if resources:
        near_res = min(resources, key=lambda r: cheb(sx, sy, r[0], r[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            d_res = cheb(nx, ny, near_res[0], near_res[1])
            d_opp = cheb(nx, ny, ox, oy)
            # Prefer reducing resource distance; avoid getting too close to opponent.
            score = -d_res * 100 - (8 - d_opp) * 3
        else:
            d_opp = cheb(nx, ny, ox, oy)
            score = d_opp * 50

        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best
    # Fallback: try any legal move deterministically
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]