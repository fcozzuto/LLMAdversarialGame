def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Defensive drift: move toward center while keeping distance from opponent
        tx, ty = w // 2, h // 2
        best = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            key = (cheb(nx, ny, ox, oy), -cheb(nx, ny, tx, ty), dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target resource: prioritize where we have the advantage in distance.
    best_target = None
    best_adv = None
    best_d_ours = None
    for rx, ry in resources:
        d_ours = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        adv = d_opp - d_ours  # positive means we're closer
        if best_adv is None or adv > best_adv or (adv == best_adv and d_ours < best_d_ours):
            best_adv = adv
            best_d_ours = d_ours
            best_target = (rx, ry)

    rx, ry = best_target

    # Greedy next step toward target, but also avoid being too close to opponent.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d_to_t = cheb(nx, ny, rx, ry)
        d_to_opp = cheb(nx, ny, ox, oy)
        # If we can capture immediately (on resource), prioritize it strongly.
        on_res = 1 if any((pr[0] == nx and pr[1] == ny) for pr in resources) else 0
        key = (on_res, -d_to_t, d_to_opp, -abs(nx - (w // 2)) - abs(ny - (h // 2)), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]