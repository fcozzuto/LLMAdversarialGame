def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if resources:
        target = min(resources, key=lambda t: (man(sx, sy, t[0], t[1]), man(ox, oy, t[0], t[1]), t[0], t[1]))
    else:
        # fallback: attack a frontier by aiming at opponent position
        target = (ox, oy)

    opp_target_bias = man(ox, oy, target[0], target[1]) - man(sx, sy, target[0], target[1])

    best = None
    best_val = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_self = man(nx, ny, target[0], target[1])
        d_opp = man(ox, oy, target[0], target[1])
        # Prefer reducing distance to target; if opponent is closer, try to reduce their advantage too.
        val = (d_self, -((d_opp - d_self) + opp_target_bias), -nx, -ny, abs(dx) + abs(dy))
        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        # last resort: deterministic safe stay
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best