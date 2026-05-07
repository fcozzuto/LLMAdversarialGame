def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    for dx, dy, nx, ny in legal:
        d_opp_here = cheb(ox, oy, nx, ny)
        # Choose the resource that maximizes our post-move advantage.
        best_adv = None
        best_self_d = None
        best_sum = None
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self  # higher is better
            # Prefer resources we can reach sooner; break ties by also considering "arrival pressure".
            s = rx + ry
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_self_d is None or d_self < best_self_d)) or (adv == best_adv and d_self == best_self_d and (best_sum is None or s < best_sum)):
                best_adv = adv
                best_self_d = d_self
                best_sum = s

        # Move selection: maximize advantage; if equal, minimize our distance to that target.
        # Add small deterministic tie-break to avoid oscillations: prefer reducing distance to opponent.
        cand = (best_adv, -best_self_d, -d_opp_here, dx, dy)
        if best is None or cand > best[0]:
            best = (cand, dx, dy)

    return [int(best[1]), int(best[2])]