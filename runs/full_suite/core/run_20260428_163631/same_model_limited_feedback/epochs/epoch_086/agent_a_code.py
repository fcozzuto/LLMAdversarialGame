def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx * dx + dy * dy) ** 0.5
    # If no resources, head toward the opponent to fight for space.
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = -1e18
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                v = -(abs(nx - tx) + abs(ny - ty)) + 0.01 * (dist(nx, ny, ox, oy) * -1)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best if best is not None else [0, 0]

    # Denial strategy: target the resource closest to the opponent (deny first).
    opp_target = min(resources, key=lambda p: dist(ox, oy, p[0], p[1]))
    # Also consider our own nearest as secondary.
    my_target = min(resources, key=lambda p: dist(sx, sy, p[0], p[1]))

    res_set = set(tuple(p) for p in resources)

    best = [0, 0]
    bestv = -1e18
    # Evaluate candidate moves.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = 0.0
            if (nx, ny) in res_set:
                v += 120.0
            # Prefer being closer to the opponent's closest resource.
            v += -2.2 * dist(nx, ny, opp_target[0], opp_target[1])
            # Secondary: improve our own resource distance slightly.
            v += -0.9 * dist(nx, ny, my_target[0], my_target[1])
            # Small tie-break: avoid getting further from both targets.
            v += 0.15 * (dist(sx, sy, opp_target[0], opp_target[1]) - dist(nx, ny, opp_target[0], opp_target[1]))
            v += 0.05 * (dist(sx, sy, my_target[0], my_target[1]) - dist(nx, ny, my_target[0], my_target[1]))
            # Mild pressure: don't drift away from opponent too much (keeps contest).
            v += -0.03 * dist(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
    # If all moves blocked (rare), stay.
    return best if best is not None else [0, 0]