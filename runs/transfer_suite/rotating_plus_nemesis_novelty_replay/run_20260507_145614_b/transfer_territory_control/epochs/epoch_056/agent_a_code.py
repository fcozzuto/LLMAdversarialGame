def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                unclaimed.append((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    cx = sx
    cy = sy
    target = None
    if unclaimed:
        target = min(unclaimed, key=lambda t: man(cx, cy, t[0], t[1]))
    elif resources:
        target = min(resources, key=lambda t: man(cx, cy, t[0], t[1]))

    best = [0, 0]
    best_val = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = cx + dx, cy + dy
            if not ok(nx, ny):
                continue
            val = 0
            if target is not None:
                val += 1000 - 10 * man(nx, ny, target[0], target[1])
            if unclaimed:
                if (nx, ny) in set(unclaimed):
                    val += 500
            if resources:
                if (nx, ny) in set(resources):
                    val += 300
            # Avoid moving too close to opponent
            dfo = man(nx, ny, ox, oy)
            val += min(200, dfo * 20)
            # Tiny deterministic tie-break toward staying closer to center
            val -= abs((nx - (w - 1) / 2.0)) + abs((ny - (h - 1) / 2.0))
            if val > best_val:
                best_val = val
                best = [dx, dy]

    if best == [0, 0]:
        # deterministic fallback: try any valid neighbor
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if dx == 0 and dy == 0:
                    continue
                if ok(nx, ny):
                    return [dx, dy]
        return [0, 0]
    return best