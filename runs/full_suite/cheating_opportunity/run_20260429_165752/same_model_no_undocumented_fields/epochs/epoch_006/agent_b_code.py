def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = [tuple(r) for r in observation.get("resources", [])]
    obstacles = set(tuple(o) for o in observation.get("obstacles", []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = (10**9, 0, 0)
    chose_resource = False
    if resources:
        chose_resource = True
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            target = min(resources, key=lambda r: (cheb(nx, ny, r[0], r[1]), r[0], r[1]))
            d = cheb(nx, ny, target[0], target[1])
            score = d * 2 + cheb(nx, ny, ox, oy)
            if score < best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)

    if not chose_resource:
        # No resources visible: move to increase distance from opponent while staying safe
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            score = -cheb(nx, ny, ox, oy)
            if score < best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
                best = (score, dx, dy)

    if chose_resource:
        # If we are already on a resource, stay (or nearest safe step to it if blocked)
        if (x, y) in resources:
            return [0, 0]
        dx, dy = best[1], best[2]
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]

    # Fallback: any legal move, deterministic
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]