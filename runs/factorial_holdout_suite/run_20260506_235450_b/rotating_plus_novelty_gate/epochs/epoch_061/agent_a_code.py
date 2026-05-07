def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_r = None
    best_val = -10**18
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if blocked(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Bias to resources we can reach earlier, but also prefer earlier self progress.
        val = (do - ds) * 100 - ds
        # Small tie-break: avoid targets that are "behind" obstacles relative to us (cheap local penalty).
        mx = sx + (1 if rx > sx else (-1 if rx < sx else 0))
        my = sy + (1 if ry > sy else (-1 if ry < sy else 0))
        if blocked(mx, my):
            val -= 25
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Primary: decrease distance to target; Secondary: increase relative advantage vs opponent.
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        rel = (no - ns) * 100 - ns
        # Bonus for "committing" toward target direction.
        step_dir = (1 if tx > sx else (-1 if tx < sx else 0)) * (1 if dx > 0 else (-1 if dx < 0 else 0))
        step_dir += (1 if ty > sy else (-1 if ty < sy else 0)) * (1 if dy > 0 else (-1 if dy < 0 else 0))
        rel += step_dir
        if rel > best_s:
            best_s = rel
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]