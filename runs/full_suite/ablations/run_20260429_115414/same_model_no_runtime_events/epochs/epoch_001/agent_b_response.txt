def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    mx, my = observation.get("self_position")
    ox, oy = observation.get("opponent_position")
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx > 0 else -dx if dx < 0 else 0, dy if dy > 0 else -dy if dy < 0 else 0

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(v):
        if v > 0: return 1
        if v < 0: return -1
        return 0

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        dme = dist(mx, my, rx, ry)
        dopp = dist(ox, oy, rx, ry)
        cand = (dopp - dme, -dme, rx, ry)
        if best is None or cand > best:
            best = cand
    _, _, tx, ty = best

    desired_dx = clamp(tx - mx)
    desired_dy = clamp(ty - my)

    moves = [
        (desired_dx, desired_dy), (desired_dx, 0), (0, desired_dy),
        (desired_dx, -desired_dy), (-desired_dx, desired_dy), (-desired_dx, 0), (0, -desired_dy),
        (0, 0)
    ]
    seen = set()
    ordered = []
    for dx, dy in moves:
        if (dx, dy) not in seen and -1 <= dx <= 1 and -1 <= dy <= 1:
            seen.add((dx, dy))
            ordered.append((dx, dy))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if (dx, dy) not in seen:
                seen.add((dx, dy))
                ordered.append((dx, dy))

    for dx, dy in ordered:
        nx, ny = mx + dx, my + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            if dx == desired_dx and dy == desired_dy:
                return [dx, dy]
    # fallback: pick first legal with smallest distance to target
    best_step = (10**9, 0, 0)
    for dx, dy in ordered:
        nx, ny = mx + dx, my + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = dist(nx, ny, tx, ty)
            if (d, dx, dy) < (best_step[0], best_step[1], best_step[2]):
                best_step = (d, dx, dy)
    return [best_step[1], best_step[2]]