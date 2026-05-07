def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def king(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose move that maximizes "expected claim": resources where we can arrive no later than opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy

        val = 0
        min_own = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            d1 = king(nx, ny, rx, ry)
            d2 = king(ox, oy, rx, ry)
            if d1 <= d2:
                # Prioritize immediate/secure grabs; stronger when we can be earlier.
                gap = d2 - d1
                val += 200 - 20 * d1 + 30 * gap
            else:
                # If we can't beat them, still move toward high-value choke points.
                val += 5 - 2 * d1 + max(0, 4 - (d1 - d2))

            if d1 < min_own:
                min_own = d1
            if d2 < min_opp:
                min_opp = d2

        # Encourage not giving away a resource where opponent is extremely close.
        danger = 0
        for rx, ry in resources:
            if king(ox, oy, rx, ry) == 0:
                danger = 10**6
                break
            d2 = king(ox, oy, rx, ry)
            if d2 <= 1:
                danger += 20
        val -= danger

        # Mild preference for faster overall progress to nearest resource.
        val -= 3 * min_own
        if val > best_val:
            best_val = val
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]