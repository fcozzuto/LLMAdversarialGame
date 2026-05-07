def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def pt(p):
        if isinstance(p, dict):
            if "position" in p:
                p = p["position"]
            if "x" in p and "y" in p:
                return int(p["x"]), int(p["y"])
        return int(p[0]), int(p[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        x, y = pt(p)
        if inb(x, y):
            obst.add((x, y))

    resources = [pt(r) for r in (observation.get("resources") or [])]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx + dy

    def kd(a, b, x, y):
        dx = a - x
        if dx < 0:
            dx = -dx
        dy = b - y
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    best_resource = None
    best_score = -10**18
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        score = (do - ds) * 10 - ds
        if score > best_score:
            best_score = score
            best_resource = (rx, ry)

    tx, ty = best_resource

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        ds2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        # Prefer decreasing our distance and increasing the gap vs opponent.
        val = (do2 - ds2) * 10 - ds2
        # If we step onto a resource, prioritize hard.
        if (nx, ny) in set(resources):
            val += 10**6
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]