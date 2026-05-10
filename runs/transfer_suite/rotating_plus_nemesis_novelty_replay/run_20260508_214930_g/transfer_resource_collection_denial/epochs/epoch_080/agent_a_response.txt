def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    res_set = set(resources)
    opp_set = (ox, oy)

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    # Evaluate each move by "advantage" over opponent on nearby resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in res_set:
            val += 5000

        # Focus on closest resources to keep it fast and stable.
        scored = []
        for (rx, ry) in resources:
            d1 = dist(nx, ny, rx, ry)
            if d1 > 6:
                continue
            d2 = dist(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; mildly punish those opponent can steal.
            adv = (80 // (d1 + 1)) - (60 // (d2 + 1))
            scored.append((d1, -d2, adv, rx, ry))
        if not scored:
            # Fallback: move toward the nearest resource (avoid opponent entirely).
            nearest = None
            nd = 10**9
            for (rx, ry) in resources:
                d1 = dist(nx, ny, rx, ry)
                if d1 < nd:
                    nd = d1
                    nearest = (rx, ry)
            rx, ry = nearest
            val += (200 // (nd + 1))
            # Slight anti-denial: reduce chance opponent reaches that same nearest quickly.
            d2 = dist(ox, oy, rx, ry)
            val -= (120 // (d2 + 1))
        else:
            scored.sort()
            for i in range(min(6, len(scored))):
                val += scored[i][2]
            # Micro-avoid: keep distance from opponent unless we are collecting.
            if (nx, ny) != (ox, oy):
                od = dist(nx, ny, opp_set[0], opp_set[1])
                val += (od * 3)  # prefer staying away from direct contention

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]