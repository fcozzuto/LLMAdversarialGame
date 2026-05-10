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
    rset = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                if (x, y) not in rset:
                    rset.add((x, y))
                    resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for king moves

    # Choose move that maximizes advantage for best attainable resource.
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        landing = 1 if (nx, ny) in rset else 0
        self_pos = (nx, ny)
        # Evaluate against the opponent nearest-resource response using a shared target.
        best_target_val = -10**18
        for tx, ty in resources:
            t = (tx, ty)
            ds = dist(self_pos, t)
            do = dist((ox, oy), t)
            # Prefer targets you reach first; lightly penalize longer routes.
            # Tie-break: small bias toward central-ish resources.
            center_bias = -((tx - (w-1)/2.0)**2 + (ty - (h-1)/2.0)**2) * 1e-3
            val = (do - ds) * 10.0 - ds + center_bias
            if val > best_target_val:
                best_target_val = val

        val_total = best_target_val
        if landing:
            val_total += 1000.0  # decisive for collecting this turn
        # Slightly discourage wasting steps when no immediate landing
        if not landing:
            val_total -= 0.05 * dist(self_pos, (ox, oy))
        if val_total > best_val:
            best_val = val_total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]