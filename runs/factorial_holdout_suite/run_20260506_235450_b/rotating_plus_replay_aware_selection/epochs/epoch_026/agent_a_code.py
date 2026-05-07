def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # larger is better for us
        # Prefer large advantage; then nearer target; then deterministically by coords
        key = (adv, -ds, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry), ds, do)
    (rx, ry) = best[1]

    # Move greedily toward chosen target, but keep deterministic anti-opponent tie-break
    cur_ds = cheb(sx, sy, rx, ry)
    cur_do = cheb(ox, oy, rx, ry)
    best_move = None
    for dx, dy, nx, ny in legal:
        nds = cheb(nx, ny, rx, ry)
        nodo = cur_do  # opponent stays for single-step evaluation
        # Primary: minimize our distance to target
        # Secondary: maximize our advantage (opp - our) for the next cell
        # Tertiary: prefer moves that also push opponent farther from target using their cheb from current pos if they follow best response (approx by our next move)
        adv_next = nodo - nds
        key = (-nds, adv_next, -cheb(nx, ny, ox, oy), dx, dy)
        if best_move is None or key > best_move[0]:
            best_move = (key, (dx, dy))
    return [int(best_move[1][0]), int(best_move[1][1])]