def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Candidate moves (prioritize progress: diagonals/axis steps first)
    cand = [(1, 1), (1, 0), (0, 1), (-1, 1), (1, -1), (-1, 0), (0, -1), (-1, -1), (0, 0)]
    best = (0, 0)
    bestv = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate by best contested resource we could reach best next turn (greedy, not full search)
        best_res = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we're closer
            val = 0
            if lead >= 0:
                val = 1000000 + 1000 * lead - 3 * ds
            else:
                val = - (1000 * (-lead) + 3 * ds)  # still choose something fast if no lead
            # Mild preference to reduce opponent distance to chosen resource (deny swaps)
            val -= 0.5 * (do)
            if val > best_res:
                best_res = val

        # Add small term to avoid stagnation and to favor picking up if already on a resource
        on_res = 1 if (nx, ny) in set(resources) else 0
        total = best_res + 10 * on_res - 0.1 * cheb(sx, sy, nx, ny)
        if total > bestv:
            bestv = total
            best = (dx, dy)

    # Fallback (shouldn't happen often)
    if bestv == -10**18:
        return [0, 0]
    return [int(best[0]), int(best[1])]