def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def best_res_score(x, y):
        if not resources:
            # head toward center-ish while keeping distance from opponent
            cx, cy = (w - 1) // 2, (h - 1) // 2
            return -man(x, y, cx, cy) - 0.5 * man(x, y, ox, oy)
        best = -10**18
        for rx, ry in resources:
            ds = man(x, y, rx, ry)
            do = man(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; tie -> closer.
            val = (do - ds) * 1000 - ds - do // 2
            if ds == 0:
                val += 10**9
            elif ds == 1:
                val += 10**5
            elif ds == 2:
                val += 10**3
            best = val if val > best else best
        return best

    best_move = [0, 0]
    best_val = -10**18

    # Small heuristic: if we're already very close to some resource, don't detour.
    current_best = best_res_score(sx, sy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        v = best_res_score(nx, ny)
        # discourage moving away from currently best target too aggressively
        v -= 0.01 * man(nx, ny, sx, sy)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    # If all moves blocked/invalid, stay still.
    if best_val == -10**18:
        return [0, 0]
    # If staying is competitive, prefer it to reduce flip-flopping.
    if best_move != [0, 0] and current_best + 1e4 >= best_val:
        return [0, 0]
    return best_move