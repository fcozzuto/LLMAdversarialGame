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

    # Pick resource that maximizes our relative advantage (favor collecting sooner).
    best_r = None
    best_u = -10**9
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if blocked(rx, ry):
            continue
        du = cheb(sx, sy, rx, ry)
        dov = cheb(ox, oy, rx, ry)
        u = (dov - du) * 10 - du
        # If we can collect immediately, prefer it strongly.
        if du == 0:
            u += 10**6
        # Deterministic tie-break: lowest (rx,ry)
        if u > best_u or (u == best_u and (best_r is None or (rx, ry) < best_r)):
            best_u = u
            best_r = (rx, ry)

    rx, ry = best_r if best_r is not None else resources[0]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_m = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = cheb(nx, ny, rx, ry)
        immediate = 1 if d == 0 else 0
        # Small penalty for moving away from the chosen target to reduce dithering.
        u = immediate * 10**6 - d * 10
        # Also consider relative advantage vs opponent on the chosen target.
        u += (cheb(ox, oy, rx, ry) - d)
        # Deterministic tie-break by lexicographic move preference
        if u > best_m or (u == best_m and (dx, dy) < best_move):
            best_m = u
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]