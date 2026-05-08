def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    env = observation.get("environment_name", "")

    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = []
    for r in resources:
        rx, ry = r[0], r[1]
        if inb(rx, ry) and (rx, ry) not in obs:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    best_for = {}
    for rx, ry in res:
        best_for[(rx, ry)] = md(ox, oy, rx, ry)

    # Choose move that maximizes the strongest lead to some resource (prefer winning first).
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_adv = -10**18
        for rx, ry in res:
            d_op = best_for[(rx, ry)]
            d_self = md(nx, ny, rx, ry)
            adv = d_op - d_self
            # Prefer earlier winning; slight preference for proximity to reduce tie cycles.
            val = adv * 1000 - d_self
            if env == "resource_collection":
                val += (-0.1 * (d_op - d_self == 0))
            if val > best_adv:
                best_adv = val
        # Deterministic tie-break: prefer non-still, then lexicographically smaller delta.
        still = (dx == 0 and dy == 0)
        tie = (best_adv == best_val)
        if best_adv > best_val:
            best_val = best_adv
            best_move = (dx, dy)
        elif tie:
            if still and (best_move[0] != 0 or best_move[1] != 0):
                pass
            else:
                if (dx, dy) < best_move:
                    best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]