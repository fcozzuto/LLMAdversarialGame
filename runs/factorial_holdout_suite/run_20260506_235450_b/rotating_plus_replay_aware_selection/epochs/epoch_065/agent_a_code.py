def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not resources or not legal:
        return [0, 0]

    best_key = None
    best_r = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer guaranteed/sooner wins; then best speed advantage; then deterministic tie-break
        if ds <= do:
            key = (0, do - ds, -ds, rx + ry * 0.001, rx, ry)
        else:
            key = (1, do - ds, ds - do, -do, rx + ry * 0.001, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best_move = None
    best_mkey = None
    for dx, dy, nx, ny in legal:
        nds = cheb(nx, ny, rx, ry)
        ndo = cheb(ox, oy, rx, ry)
        # Also bias toward increasing chance to beat opponent on the chosen target
        if nds <= ndo:
            mkey = (0, ndo - nds, -nds, abs(nx - rx) + abs(ny - ry), nx, ny)
        else:
            mkey = (1, ndo - nds, nds - ndo, -do, nx, ny)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]