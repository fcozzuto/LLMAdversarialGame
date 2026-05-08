def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obstacles.add((ax, ay))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = sorted(dirs, key=lambda t: (t[0], t[1]))  # deterministic

    # If evader: aim to stay far and drift toward the best corner; if pursuer: reduce distance and drift toward opponent.
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; reflect it deterministically

        dist = cheb(nx, ny, ox, oy)
        mind_corner = min(cheb(nx, ny, cx, cy) for cx, cy in corners)

        # Centering term helps against zigzag by reducing perimeter hugging.
        center = (w // 2, h // 2)
        center_dist = cheb(nx, ny, center[0], center[1])

        # Deterministic tie-break uses dx,dy lexicographic via iteration order.
        if is_evader:
            score = (dist * 100) + (mind_corner * 2) - (center_dist)  # maximize distance/corner proximity, avoid center less
            better = best is None or score > best_score
        else:
            score = (-(dist * 100)) + (-mind_corner) + (center_dist // 2)  # minimize distance; mild anti-cornering
            better = best is None or score > best_score

        if better:
            best = (dx, dy)
            best_score = score

    return [int(best[0]), int(best[1])]